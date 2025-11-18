import os
import subprocess
import shutil
import json
import sqlite3
from PIL import Image
from slugify import slugify

from fit_files_to_geojson_merge import parse_and_merge_fit_files


def add_images_to_trip(cursor: sqlite3.Cursor, trip_id : int | None, all_files_in_dir : list[str], full_path_to_dir: str) -> None:
    '''
    Prompts the user for the path to the directory with images and then adds them to the trip
    '''

    valid_extensions = ('.jpeg', '.jpg', '.png')

    images_to_add : list[str] = []

    # Only add images 
    for file in all_files_in_dir:
        if file.lower().endswith(valid_extensions):
            images_to_add.append(file)


    # Add optional mp4 video file if it exists
    mp4_video_filename = None
    for file in all_files_in_dir:

        if file.lower().endswith('.mp4'):
            mp4_video_filename = file


    if mp4_video_filename is not None:



        # Copy the video to the project directory

        full_path = os.path.join(full_path_to_dir, mp4_video_filename)

        project_videso_dir = '/Users/dava/Projects/web_dev/my_website/static/videos'

        dest_path = os.path.join(project_videso_dir, mp4_video_filename)


        # --- Compress full video (with faststart for web playback) ---
        compress_cmd = [
            "ffmpeg",
            "-y",
            "-i", full_path,
            "-vcodec", "libx264",
            "-preset", "slow",
            "-crf", "28",
            "-acodec", "aac",
            "-b:a", "128k",
            "-vf", "scale='min(1280,iw)':'min(720,ih)'",
            "-movflags", "+faststart",
            dest_path
        ]
        subprocess.run(compress_cmd, check=True)


        insert_statement = '''
            UPDATE trips
            SET trip_video_filename = ?
            WHERE trip_id = ?
            '''

        cursor.execute(insert_statement, (mp4_video_filename, trip_id))

        print("Compressed and inserted the video")



    # Proccess found images
    main_image_exists = False

    for image_filename in images_to_add:
        input_path = os.path.join(full_path_to_dir, image_filename)


        if image_filename.lower().startswith('main'):
            is_main = 1
            main_image_exists = True

            project_compressed_previews_dir = '/Users/dava/Projects/web_dev/my_website/static/images/compressed_previews' 
            output_path = os.path.join(project_compressed_previews_dir, image_filename)

            # Compress and save images to images/compressed_previews too
            quality = 5 

            # Run FFmpeg compression
            cmd = [
                "ffmpeg",
                "-y",  # overwrite existing output
                "-i", input_path,
                "-vf", "scale='if(gt(iw,ih),1600,-1)':'if(gt(ih,iw),1600,-1)'",
                "-q:v", str(quality),
                output_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
        else:
            is_main = 0


        project_compressed_images_dir = '/Users/dava/Projects/web_dev/my_website/static/images/compressed'

        output_path = os.path.join(project_compressed_images_dir, image_filename)

        # Compress and save images to images/compressed
        quality = 2 

        # Run FFmpeg compression
        cmd = [
            "ffmpeg",
            "-y",  # overwrite existing output
            "-i", input_path,
            "-vf", "scale='if(gt(iw,ih),1600,-1)':'if(gt(ih,iw),1600,-1)'",
            "-q:v", str(quality),
            output_path
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


        # Figure out the dimensions of the image
        image_file = Image.open(output_path)
        image_width, image_height = image_file.size

        insert_statement = '''
                INSERT INTO trips_images
                (trip_id, image_filename, is_main, image_width, image_height)
                VALUES (?,?,?,?,?)
                '''

        cursor.execute(insert_statement, (trip_id, image_filename, is_main, image_width, image_height))

    if not main_image_exists and not mp4_video_filename:
        raise Exception("No main image or main video was found in the directory! Aborting")
    


def test_query_id(cursor: sqlite3.Cursor, row_id : int) -> bool:
    '''
    Querries the database for the newly added ID to check if it was added successfully
    Prompts user to confirm if the row was added successfully or not 
    '''
    query = ''' SELECT * from trips WHERE trip_id = ?'''

    newly_added_trip = dict(cursor.execute(query, (row_id,)).fetchone())

    # Print out the values for checking purposes
    print("The last row added:")

    for k,v in newly_added_trip.items():
        print(f"{k}: {v}")


    while True:
        confirm = input("The trip was inserted as expected?[y/n]\n").strip()

        if confirm.lower() == 'y':
            return True
        if confirm.lower() == 'n':
            return False   


def insert_trip_to_db(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    '''
    Inserts the trip along with its images to the database after parsing the .fit file 
    and converting all values to the appropriate format
    '''

    # Prompt for the absolute path of the directory with images and .fit file
    while True:

        full_path_to_dir = input("Full absolute path to the directory with images and .fit file of the trip to add: ").strip('\'')

        if os.path.isdir(full_path_to_dir):
            print("Directory exists. Safe to insert")
            break
        else:
            print('Directory was not found! Check the path.')

    all_files_in_dir = os.listdir(full_path_to_dir)


    # Find and read the description file     

    for file in all_files_in_dir:
        if file.lower().startswith('description'):
            description_file = os.path.join(full_path_to_dir, file)

    if description_file is None:
        raise Exception("No description file found in the directory!")

    with open(description_file, 'r', encoding='utf-8') as file:
        # Txt document structure : 
        # [Name...]
        # Description: [Description...]
        text = file.read().strip()

        # Split at 'Description:'
        parts = text.split("Description:", 1)

        name = parts[0].strip()  
        trip_slug = slugify(name)

        if len(parts) > 1:
            description = parts[1].strip()
        else:
            description = ""

    # Do the work on .fit files to merge and extract all the data needed for insertion 
    merged_stats_and_route = parse_and_merge_fit_files(all_files_in_dir=all_files_in_dir, full_path_to_dir=full_path_to_dir)

    ride_values_to_insert = (
        name,
        trip_slug,
        description,
        merged_stats_and_route['start_time'],
        merged_stats_and_route['avg_speed'],
        merged_stats_and_route['max_speed'],
        merged_stats_and_route['distance'],
        merged_stats_and_route['total_time'],
        merged_stats_and_route['moving_time'],
        merged_stats_and_route['total_ascent'],
        merged_stats_and_route['total_descent'],
        merged_stats_and_route['geojson_filename']
    )

    # Insert the tuple into the database

    insert_statement = ''' INSERT INTO trips 
                    (trip_name, trip_slug, trip_description, start_time, avg_speed, max_speed, distance, total_time, moving_time,
                    total_ascent, total_descent, geojson_filename)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    '''

    cursor.execute(insert_statement, ride_values_to_insert)

    newly_added_trip_id = cursor.lastrowid

    # Update the fts table too
    cursor.execute('''
        INSERT INTO trips_fts(rowid, trip_name, trip_description)
        VALUES (?, ?, ?)
    ''',(
        newly_added_trip_id,       # rowid
        ride_values_to_insert[0],  # trip_name (first element of the tuple)
        ride_values_to_insert[2]   # trip_description (third element of the tuple)
    ))



    # Add images to the trip
    add_images_to_trip(cursor=cursor, trip_id=newly_added_trip_id, all_files_in_dir=all_files_in_dir, full_path_to_dir=full_path_to_dir)
            
    # Test if the row was added correctly
    successfully_added = test_query_id(cursor=cursor, row_id=newly_added_trip_id)


    if successfully_added:
        connection.commit()
        print("\nThe trip was commited to the database")
    else:
        print("\nInsert aborted, nothing was saved to the database")
        connection.close()

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



