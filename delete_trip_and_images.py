import sqlite3
import os

with sqlite3.connect("trips.db") as conn:

    try:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        trip_to_delete = None

        while True:

            trip_id_to_delete = input("Trip ID to delete['last' to delete last trip]: \n")

            if trip_id_to_delete.lower() == 'last':
                # Get the last trip_id
                cursor.execute("SELECT * FROM trips ORDER BY trip_id DESC LIMIT 1")
                break

            else:
                cursor.execute(f"SELECT * FROM trips WHERE trip_id == {trip_id_to_delete}")
                break

        trip_to_delete = cursor.fetchone()

        trip_id_to_delete = trip_to_delete['trip_id']

        gejson_filename = trip_to_delete['geojson_filename']

        path_to_geojson = os.path.join('./static/geo_json', gejson_filename)

        if os.path.exists(path_to_geojson):
            os.remove(path_to_geojson)

        else:
            print("Could not find the geojson file! Not deleted")
        
        if trip_id_to_delete:
            # Get all image filenames to delete the files later
            cursor.execute("SELECT image_filename FROM trips_images WHERE trip_id = ?", (trip_id_to_delete,))

            image_files = [row['image_filename'] for row in cursor.fetchall()]

            # Delete images from DB
            cursor.execute("DELETE FROM trips_images WHERE trip_id = ?", (trip_id_to_delete,))

            # Delete image files from disk
            for filename in image_files:
                path = os.path.join('./static/images', filename)
                if os.path.exists(path):
                    os.remove(path)
                else:
                    print("Could not find the image! Not deleted")

            print(f"Trip {trip_id_to_delete} and its images have been deleted.")


            # Delete video if exists
            video_row = cursor.execute(
                "SELECT trip_video_filename FROM trips WHERE trip_id = ?", (trip_id_to_delete,)
            ).fetchone()

            video_filename = video_row['trip_video_filename'] if video_row else None

            if video_filename is not None:
            
                path = os.path.join('./static/videos', video_filename)
                if os.path.exists(path):
                    os.remove(path)
                    print("Deleted the video from the disk")
                else:
                    print("Could not find the video file! Not deleted")

            else:
                print("No vide filename associated with the trip...")

            # Delete trip from DB
            print("Deleting the trip itself from the database...")
            cursor.execute("DELETE FROM trips WHERE trip_id = ?", (trip_id_to_delete,))

            conn.commit()
            
    except Exception as e:
        print(e)
        if conn:
            conn.close()
