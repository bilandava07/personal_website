import sqlite3
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
                total_descent FLOAT NOT NULL
            )
        ''')

        connection.execute('''
            CREATE TABLE IF NOT EXISTS trips_images(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                is_main BOOLEAN DEFAULT 0,
                FOREIGN KEY (trip_id)  REFERENCES trips(trip_id)
            )
        ''')

        connection.commit()


def get_all_trips_with_main_images(cursor: sqlite3.Cursor, order_by : str = 'DESC'):
    '''
    Querries the database for all trips and their ids and names
    Does so by taking into account user's ordering preference 
    for now Duration ASC or Duration DESC
    '''

    if order_by.upper() not in ('ASC', 'DESC'):
        # Default to descending order if parameter is invalid
        order_by = 'DESC'
    querry = f'''
        SELECT trips.trip_id, trips.trip_name, trips_images.image_path 
        FROM trips
        LEFT JOIN trips_images ON trips.trip_id = trips_images.trip_id 
        AND trips_images.is_main = 1
        ORDER BY trips.total_time {order_by}
    '''

    return cursor.execute(querry).fetchall()

init_db(TRIPS_DATABASE)





@app.route('/')
def home_page():
    '''Renders the home page'''
    return render_template('home_page.html')

@app.route('/cycling')
def cycling_page():
    ''' Renders the main cycling page '''

    cursor = get_db(TRIPS_DATABASE).cursor()

    trips_preview = get_all_trips_with_main_images(cursor=cursor)



    return render_template('cycling_page.html', trips_preview = trips_preview)


@app.teardown_appcontext
def close_connection(exception):
    # Closes the connection to the database when the request is over
    for attr in list(g.__dict__.keys()):
        if attr.startswith('_db_'):
            db = getattr(g, attr)
            if db is not None:
                db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

