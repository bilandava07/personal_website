import sqlite3
from slugify import slugify
from zoneinfo import ZoneInfo
from datetime import datetime
from flask import Flask, render_template, g

app = Flask(__name__)

TRIPS_DATABASE = 'trips.db'

def get_db(db_name):

    '''Connects to the database'''
    #Safely connects to and returns the database
    attr_name = f'_db_{db_name}'

    db = getattr(g, '_database', None) # Check if a connection already exists for this request
    if db is None:
        db = g._database = sqlite3.connect(db_name) # Create a new connection if needed
        db.row_factory = sqlite3.Row # Make rows dict-like for ease of use in queries 
        setattr(g, attr_name, db)
    return db


def init_db(db_name):
    '''Initializes the tables by creating them if they do not exist already'''

    with sqlite3.connect(db_name) as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS trips(
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                avg_speed FLOAT NOT NULL,
                max_speed FLOAT NOT NULL,
                distance FLOAT NOT NULL,
                total_time FLOAT NOT NULL,
                moving_time FLOAT NOT NULL,
                total_ascent FLOAT NOT NULL,
                total_descent FLOAT NOT NULL,
                geojson_filename TEXT NOT NULL
            )
        ''')

        connection.execute('''
            CREATE TABLE IF NOT EXISTS trips_images(
                image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                image_filename TEXT NOT NULL,
                is_main BOOLEAN DEFAULT 0,
                image_width INT NOT NULL,
                image_height INT NOT NULL,
                FOREIGN KEY (trip_id)  REFERENCES trips(trip_id)
            )
        ''')

        connection.commit()

def convert_trip_stats(raw_trip) -> dict:
    ''' Converts trip's values to the right format for presentation on the frontend '''

    avg_speed_kmh = round(raw_trip['avg_speed'] * 3.6, 1)
    max_speed_kmh = round(raw_trip['max_speed'] * 3.6, 1)

    distance_km = round(raw_trip['distance'] / 1000, 1)

    # convert time from seconds to respective formats

    total_time_hr = round(raw_trip['total_time'] / 3600)
    total_time_min = round((raw_trip['total_time'] % 3600) / 60)

    total_time_formatted = f"{total_time_hr} h {total_time_min} m"

    moving_time_hr = round(raw_trip['moving_time'] / 3600)
    moving_time_m = round((raw_trip['moving_time'] % 3600) / 60)

    moving_time_formatted = f"{moving_time_hr} h {moving_time_m} m"


    # Convert to local timezone
    start_time_utc = datetime.fromisoformat(raw_trip['start_time'])
    start_time_utc = start_time_utc.replace(tzinfo=ZoneInfo("UTC"))
    local_tz = ZoneInfo("Europe/Berlin")  # change to your timezone
    start_time_local = start_time_utc.astimezone(local_tz)
    # Display format 
    start_date_time_formatted = start_time_local.strftime("%d %B %Y at %H:%M")


    paused_seconds = raw_trip['total_time'] - raw_trip['moving_time']
    paused_time_hr = paused_seconds // 3600
    paused_time_min = (paused_seconds % 3600) // 60
    paused_time_formatted = f"{paused_time_hr} h {paused_time_min} m"


    # Return formatted data ready to display on the frontend 
    return {
        "trip_name" : raw_trip["trip_name"],
        "trip_id" : raw_trip["trip_id"],
        "avg_speed_kmh" : avg_speed_kmh,
        "max_speed_kmh" : max_speed_kmh,
        "distance_km" : distance_km,
        "total_time_formatted" : total_time_formatted,
        "moving_time_formatted" : moving_time_formatted,
        "start_date_time_formatted" : start_date_time_formatted,
        "paused_time_formatted" : paused_time_formatted,
        "total_ascent" : raw_trip['total_ascent'],
        "total_descent" : raw_trip['total_descent'],
        "geojson_filename" : raw_trip['geojson_filename']
    }


def get_all_trips_with_main_images(cursor: sqlite3.Cursor, order_by : str = 'DESC') -> list[any]:
    '''
    Querries the database for all trips and their ids and names
    Does so by taking into account user's ordering preference 
    for now Duration ASC or Duration DESC
    '''

    if order_by.upper() not in ('ASC', 'DESC'):
        # Default to descending order if parameter is invalid
        order_by = 'DESC'
    querry = f'''
        SELECT   
            trips.trip_id,
            trips.trip_name,
            trips_images.image_id,
            trips_images.image_filename,
            trips_images.is_main
        FROM trips
        LEFT JOIN trips_images ON trips.trip_id = trips_images.trip_id 
        AND trips_images.is_main = 1
        ORDER BY trips.total_time {order_by}
    '''
    trip_overview = cursor.execute(querry).fetchall()

    return trip_overview

    # # List of tuples where each tuple is a trip 
    # trips_converted = []


    # # Convert the trips to the right format
    # for raw_trip in raw_trips:
    #     trips_converted.append(convert_trip_stats(raw_trip=raw_trip))

    # return trips_converted


def get_trip_info(cursor: sqlite3.Cursor, trip_id:int) -> dict | None :
    '''
    Querries the database for one specific trip by ID to
    then display it on the trip_page'''

    trip_querry = '''
        SELECT   
            trips.trip_id,
            trips.trip_name,
            trips.start_time,
            trips.avg_speed,
            trips.max_speed,
            trips.distance,
            trips.total_time,
            trips.moving_time,
            trips.total_ascent,
            trips.total_descent,
            trips.geojson_filename
        FROM trips
        WHERE trips.trip_id = ?
    '''
    raw_trip = cursor.execute(trip_querry, (trip_id,)).fetchone()

    if raw_trip is None:
        return None
    else:
        converted_trip = convert_trip_stats(raw_trip=raw_trip)

    images_querry = '''
        SELECT
            i.image_id, 
            i.trip_id, 
            i.image_filename, 
            i.is_main,
            i.image_width, 
            i.image_height
        FROM trips_images as i
        WHERE i.trip_id = ?
    '''

    trip_images = cursor.execute(images_querry, (trip_id,)).fetchall()

    converted_trip["images"] : list[dict] = []
    for trip_image in trip_images:

        if trip_image["image_width"] > trip_image["image_height"]:
            photo_class = "wide"

        elif trip_image["image_height"] > trip_image["image_width"]:
            photo_class = "tall"
        else:
            photo_class = "square"

        trip_image_dict = {
            "image_id" : trip_image["image_id"],
            "trip_id" : trip_image["trip_id"],
            "image_filename" : trip_image["image_filename"],
            "is_main" : bool(trip_image["is_main"]),
            "image_width" : trip_image["image_width"],
            "image_height" : trip_image["image_height"],
            "photo_class" : photo_class

        }

        converted_trip["images"].append(trip_image_dict)

    return converted_trip


init_db(TRIPS_DATABASE)





@app.route('/')
def home_page():
    '''Renders the home page'''
    return render_template('home_page.html')

@app.route('/cycling')
def cycling_page():
    ''' Renders the main cycling page '''

    cursor = get_db(TRIPS_DATABASE).cursor()

    rides_previews = get_all_trips_with_main_images(cursor=cursor)

    return render_template('cycling_page.html', rides = rides_previews)


@app.route('/trip/<int:trip_id>')

def trip_page(trip_id : int):
    '''Renders one trip's page with stats, photos, a map etc.'''
    cursor = get_db(TRIPS_DATABASE).cursor()

    trip_data = get_trip_info(cursor=cursor, trip_id=trip_id)

    for image in trip_data["images"]:
        if image["is_main"]:
            main_image = image

    regular_images = [img for img in trip_data["images"] if not img["is_main"]]

    return render_template('trip_page.html', trip = trip_data, main_image = main_image, regular_images = regular_images )

@app.teardown_appcontext
def close_connection(exception):
    ''' Closes the connection to the database when the request is over '''
    for attr in list(g.__dict__.keys()):
        if attr.startswith('_db_'):
            db = getattr(g, attr)
            if db is not None:
                db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

