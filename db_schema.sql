'''Initiallt used for planning to makes drafts of the tables, actual table definitions in flask_app.py'''

CREATE TABLE IF NOT EXISTS trips(
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_name TEXT NOT NULL,
    trip_video_filename TEXT,
    trip_slug TEXT NOT NULL,
    trip_description TEXT NOT NULL,
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

CREATE TABLE IF NOT EXISTS trips_images(
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    image_filename TEXT NOT NULL,
    is_main BOOLEAN DEFAULT 0,
    image_width INT NOT NULL,
    image_height INT NOT NULL,
    FOREIGN KEY (trip_id)  REFERENCES trips(trip_id)
)
