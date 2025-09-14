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


CREATE TABLE IF NOT EXISTS trips_images(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    is_main BOOLEAN DEFAULT 0,
    FOREIGN KEY (trip_id)  REFERENCES trips(id)

)



-- Querry to get the names and main images of all tripsj
SELECT trips.trip_name, trips_images.image_path 
FROM trips
LEFT JOIN trips_images ON trips.id = trips_images.trip_id 
AND trips_images.is_main = 1

 