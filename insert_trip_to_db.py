import os
import uuid
import json
from datetime import datetime
import sqlite3
from zoneinfo import ZoneInfo
from fitparse import FitFile


def add_image_to_trip(cursor: sqlite3.Cursor, trip_id : int | None, is_main : int | None) -> bool:
    '''
    Promts the user for the image path of the image to be inserted to the trip
    inserts the image to the trips_images table 
    '''

    if not trip_id:
        # Prompt the user for trip_id if the function is being used to manually
        # add an image to an already existing trip 
        trip_id = input("ID of the trip the image is being added to: ")

    while True:

        image_path = input("Name of the image to be added: ")

        # Join the folder path and the filename
        full_path = os.path.join('static', 'images', image_path)

        if os.path.isfile(full_path):
            print("File exists. Safe to insert")
            break
        else:
            print('File does not exist on the disk! File should exist in [static/images/img_name.jpeg]')




    if is_main not in (1, 0, None):
        # Prompt the user for the is_main attribute
        while True:
            is_main = input("Is the picture the main of the trip? [y/n]")

            if isinstance(is_main, str):
                if is_main.lower() == 'y':
                    is_main = 1
                    break
                elif is_main.lower() == 'n':
                    is_main = 0
                    break

    insert_statement = '''INSERT INTO trips_images (trip_id, image_filename, is_main) VALUES (?,?,?)'''

    cursor.execute(insert_statement, (trip_id, image_path, is_main))


def test_querry_id(cursor: sqlite3.Cursor, row_id : int) -> bool:
    '''
    Querries the database for the newly added ID to check if it was added successfully
    Prompts user to confirm if the row was added successfully or not 
    '''

    querry = ''' SELECT * from trips LEFT JOIN trips_images USING (trip_id) WHERE trips.trip_id = ?'''

    cursor.execute(querry, (row_id,))
    newly_added_trip = dict(cursor.fetchone())

    # Print out the values for checking purposes
    print("The last row added:")

    for k,v in newly_added_trip.items():
        print(f"{k}: {v}")


    while True:
        confirm = input("The trip was inserted as expected?[y/n]\n")

        if isinstance(confirm, str):
            if confirm.lower() == 'y':
                return True
            elif confirm.lower() == 'n':
                return False   


def insert_trip_to_db(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    '''
    Inserts the trip to the database after parsing the .fit file 
    and converting all values to the appropriate format
    '''

    # fitfile = FitFile('rides_fit/' + input("Name of the fit file to parse and get data from: "))

    # Testing file to avoid having to paste the name everytime
    fitfile = FitFile('rides_fit/' + "2025-09-12-160814-ELEMNT ROAM B53E-57-0.fit")

    # Prompt the user for the name of the trip
    confirmed = False

    while not confirmed:
        name = input("What should the name for this ride be: ")

        confirm = input(f"Name: {name}\nAre you sure this is the name you want to use? [y]\n")

        if confirm.lower() == 'y':
            confirmed = True

    # Parses the .fit file and returns a readable json with name and values of the fit fields
    for session in fitfile.get_messages('session'):
        ride_data = {}
        for field in session:
            ride_data[field.name] = field.value

    print(ride_data)

    # Extract the route from the .fit file
    raw_route_coordinates = []

    for record in fitfile.get_messages('record'):
        # Convert the time_stamp to seconds right away to be able to do math on them later
        
        time_stamp = datetime.fromisoformat(str(record.get_value('timestamp')))
        lon = record.get_value('position_long')
        lat = record.get_value('position_lat')

        # Convert the semicircles to degrees
        if lat is not None and lon is not None:
            lon_deg = lon * (180 / 2**31)
            lat_deg = lat * (180 / 2**31)

            raw_route_coordinates.append((time_stamp, lon_deg, lat_deg))


    
    # Filter the coordinates to only leave one coordinate every [interval] seconds
    filtered_route_coordinates = []

    last_ts = None

    interval = 10 # seconds

    for coordinate in raw_route_coordinates:
        current_ts = coordinate[0] # datetime object

        # Initialize last_ts
        if last_ts is None:
            # Always add the first point
            filtered_route_coordinates.append((coordinate[1], coordinate[2]))
            last_ts = coordinate[0]
            continue


        # Add if interval has passed
        if (current_ts - last_ts).total_seconds() >= interval:
            # If reached interval, only append the lat and long
            filtered_route_coordinates.append((coordinate[1],coordinate[2]))
            last_ts = current_ts



    # Create GeoJSON file using the coordinates
    geojson_dict = {
    "type": "Feature",
    "geometry": {
        "type": "LineString",
        "coordinates": filtered_route_coordinates
        }
    }

    route_geo_json = json.dumps(geojson_dict)

    # Generate random unique name
    geojson_filename = f"{uuid.uuid4().hex}.geojson"

    folder = "static/geo_json"

    # Full path to the file
    geo_json_path = os.path.join(folder, geojson_filename)

    # Write the route GeoJSON to the file to reference it later
    with open(geo_json_path, 'w') as file:
        file.write(route_geo_json)



    # Get the data to insert to the table from the json

    # Store the start time in the ISO 8601 format
    start_time_utc = ride_data['start_time']  # naive datetime from FIT
    start_time_utc = start_time_utc.replace(tzinfo=ZoneInfo("UTC"))

    # Convert to local timezone
    local_tz = ZoneInfo("Europe/Berlin")
    start_time_local = start_time_utc.astimezone(local_tz)

    start_time_str = start_time_local.strftime("%Y-%m-%d %H:%M:%S")

    # Get the rest of the metrics as is (maybe other formats later?)
    avg_speed = ride_data['avg_speed']
    max_speed = ride_data['max_speed']

    distance = ride_data['total_distance']

    total_time_s = ride_data['total_elapsed_time']
    moving_time = ride_data['total_timer_time']

    total_ascent = ride_data['total_ascent']
    total_descent = ride_data['total_descent']

    # Store all the needed data in a tuple for insertion
    ride_values_to_insert = (
        name,
        start_time_str,
        avg_speed,
        max_speed,
        distance,
        total_time_s,
        moving_time,
        total_ascent,
        total_descent,
        geojson_filename
    )

    # Testing purposes confirmation prompt

    # print(ride_values_to_insert)

    # confirmed = False

    # while not confirmed:
    #     confirm = input("Those are values that will be inserted into the databased, procceed? [y]\n")
    #     if confirm.lower() == 'y':
    #         confirmed = True

    # Insert the tuple into the database

    insert_statement = ''' INSERT INTO trips 
                    (trip_name, start_time, avg_speed, max_speed, distance, total_time, moving_time,
                    total_ascent, total_descent, geojson_filename)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    '''

    cursor.execute(insert_statement, ride_values_to_insert)

    newly_added_trip_id = cursor.lastrowid


    adding_images = True

    while adding_images:
        add_main_img_input = input("Add main image to the trip? [y/n]\n")
        if isinstance(add_main_img_input, str):
            if add_main_img_input.lower() == 'y':
                add_image_to_trip(cursor=cursor, trip_id=newly_added_trip_id, is_main=1)

                # TODO: Add other regular images loop 
                # (maybe image paths separated by commas and then split on comma list)
                break


            elif add_main_img_input.lower() == 'n':
                adding_images = False
            
    # Test if the row was added correctly
    successfully_added = test_querry_id(cursor=cursor, row_id=cursor.lastrowid)


    if successfully_added:
        connection.commit()
        print("\nThe trip was commited to the database")
    else:
        connection.rollback()
        print("\nInsert aborted, nothinb was saved to the database")
    




if __name__ == '__main__':
    # Establish connectin to the database
    DB = 'trips.db'
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        insert_trip_to_db(connection=connection, cursor=cursor)
    except Exception as e:
        if connection:
            connection.rollback()
        print("Error: ", e)

    finally:
        if connection:
            connection.close()




