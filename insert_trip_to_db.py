import sqlite3
from zoneinfo import ZoneInfo
from fitparse import FitFile

def add_image_to_trip()

def test_querry_id(cursor: sqlite3.Cursor, row_id : int) -> bool:
    '''
    Querries the database for the newly added ID to check if it was added successfully
    Prompts user to confirm if the row was added successfully or not 
    '''

    querry = ''' SELECT * from trips WHERE trips.id = ?'''

    cursor.execute(querry, (row_id,))
    newly_added_trip = dict(cursor.fetchone())

    # Print out the values for checking purposes
    print("The last row added:")

    for k,v in newly_added_trip.items():
        print(f"{k}: {v}")


    while True:
        confirm = input("The trip was inserted as expected?[y/n]")
        if confirm.lower() == 'y':
            return True
        elif confirm.lower() == 'n':
            return False   


def insert_trip_to_db(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    '''
    Inserts the trip to the database after parsing the .fit file 
    and converting all values to the appropriate format
    '''

    fitfile = FitFile('rides_fit/' + input("Name of the fit file to parse and get data from: "))

    # Parses the .fit file and returns a readable json with name and values of the fit fields
    for session in fitfile.get_messages('session'):
        ride_data = {}
        for field in session:
            ride_data[field.name] = field.value

    print(ride_data)

    # Prompt user for trip_name and confirmation

    confirmed = False

    while not confirmed:
        name = input("What should the name for this ride be: ")

        confirm = input(f"Name: {name}\nAre you sure this is the name you want to use? [y]\n")

        if confirm.lower() == 'y':
            confirmed = True


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
        total_descent
    )

    print(ride_values_to_insert)

    confirmed = False

    while not confirmed:
        confirm = input("Those are values that will be inserted into the databased, procceed? [y]\n")
        if confirm.lower() == 'y':
            confirmed = True

    # Insert the tuple into the database



    insert_statement = ''' INSERT INTO trips 
                    (trip_name, start_time, avg_speed, max_speed, distance, total_time, moving_time,
                    total_ascent, total_descent)
                    VALUES (?,?,?,?,?,?,?,?,?)
                    '''

    cursor.execute(insert_statement, ride_values_to_insert)

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




