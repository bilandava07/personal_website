import os
from fitparse import FitFile
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo
import uuid
import json


def sort_fit_files_dicts(fitfiles_dicts : list[dict]) -> list[dict]:

    '''Sorts the fitfiles dict by the first timestamp'''
    return sorted(
        fitfiles_dicts,
        key=lambda fitfile_dict : fitfile_dict.get('start_time')
    )




def merge_and_convert_the_stats(rides_data_dicts_sorted : list[dict]) -> dict:

    '''
    Takes a SORTED list with dicts with ride data in them 
    Merges the stats bu logically infering each one of them 
    Converts the merged stats along the way to the format
    that is supposed to be stored in the database
    '''

    merged_stats : dict = {}

    # Start time should be the start time of the first ride in the list

    # Store the start time in the ISO 8601 format
    start_time_utc = rides_data_dicts_sorted[0]['start_time']  # naive datetime from FIT
    start_time_utc = start_time_utc.replace(tzinfo=ZoneInfo("UTC"))

    # Convert to local timezone
    local_tz = ZoneInfo("Europe/Berlin")
    start_time_local = start_time_utc.astimezone(local_tz)

    start_time_str = start_time_local.strftime("%Y-%m-%d %H:%M:%S")

    merged_stats['start_time'] = start_time_str

    merged_stats['distance'] = sum(ride_data_dict['total_distance'] for ride_data_dict in rides_data_dicts_sorted)

    merged_stats['total_time'] = sum(ride_data_dict['total_elapsed_time'] for ride_data_dict in rides_data_dicts_sorted)

    merged_stats['moving_time'] = sum(ride_data_dict['total_timer_time'] for ride_data_dict in rides_data_dicts_sorted)

    merged_stats['max_speed'] = max(ride_data_dict['max_speed'] for ride_data_dict in rides_data_dicts_sorted)

    merged_stats['total_ascent'] = sum(ride_data_dict['total_ascent'] for ride_data_dict in rides_data_dicts_sorted)

    merged_stats['total_descent'] = sum(ride_data_dict['total_descent'] for ride_data_dict in rides_data_dicts_sorted)

    merged_stats['avg_speed'] = merged_stats['distance'] / merged_stats['moving_time']

    return merged_stats






def merge_coordinates_lists(raw_routes_coordinates: list[list[tuple]]) -> list[tuple]:
    ''' Merges multiple lists with corrdinates to one in order'''
    merged_coordinates: list[tuple] = []

    for route_coordinates in raw_routes_coordinates:
        merged_coordinates.extend(route_coordinates) 
    return merged_coordinates


def filter_coordinates_by_interval(raw_route_coordinates: list[tuple], interval : int = 10) -> list[tuple]:
    '''
    Takes in a list with coordinates and filters them to only leave one coordinate pro given interval
    '''

    # Filter the coordinates to only leave one coordinate every [interval] seconds
    filtered_route_coordinates = []

    last_ts = None

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

    return filtered_route_coordinates


def parse_and_merge_fit_files(all_files_in_dir: list[str], full_path_to_dir: str):
    '''
    Searches the directory for all .fit files 
    Extracts the data needed for display and merges this data
    from all .fit files to one geo json file
    '''

    merged_and_converted_ride : dict = {}


    # Iterate through the directory and find all the .fit files 
    fitfiles : list[FitFile] = []

    for file in all_files_in_dir:
        if file.lower().endswith('.fit'):
            path_to_fit_file = os.path.join(full_path_to_dir, file)
            fitfiles.append(FitFile(path_to_fit_file))

        
    if len(fitfiles) == 0:
        raise Exception("No .fit files were found in the directory!")
    


    # Parses the .fit files and returns readable dicts with names and values of the fit fields
    all_rides_data_dicts : list[dict] = []
    counter = 0

    for fitfile in fitfiles:

        for session in fitfile.get_messages('session'):
            ride_data = {}
            for field in session:
                ride_data[field.name] = field.value


            # Parse record messages (coordinates) for this file
            ride_records = []
            for record in fitfile.get_messages('record'):
                ts = record.get_value('timestamp')
                lon = record.get_value('position_long')
                lat = record.get_value('position_lat')

                if ts is not None and lon is not None and lat is not None:
                    lon_deg = lon * (180 / 2**31)
                    lat_deg = lat * (180 / 2**31)
                    ride_records.append((ts, lon_deg, lat_deg))

            # Attach records as a new key
            ride_data['records'] = ride_records

            
            counter += 1

            all_rides_data_dicts.append(ride_data)

            print(f"Parsed the .fit file number {counter}\n\n\n")



    
    # Sort the .fit files by first start time
    all_rides_data_dicts_sorted = sort_fit_files_dicts(fitfiles_dicts=all_rides_data_dicts)

    # Merge all rides dicts 
    # 1. Merge the stats
    merged_and_converted_ride = merge_and_convert_the_stats(rides_data_dicts_sorted=all_rides_data_dicts_sorted)

    # 2. Merge the coordinates for the map 
    raw_routes_coordinates = [ride_data['records'] for ride_data in all_rides_data_dicts_sorted]

    merged_coordinates = merge_coordinates_lists(raw_routes_coordinates=raw_routes_coordinates)

    filtered_merged_coordinates = filter_coordinates_by_interval(raw_route_coordinates=merged_coordinates, interval=10)

    # Create GeoJSON file of the route using the filtered merged coordinates
    geojson_dict = {
    "type": "Feature",
    "geometry": {
        "type": "LineString",
        "coordinates": filtered_merged_coordinates
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


    #3. Add the merged and filtered route coordinates in geo_json to merged and converted route stats

    merged_and_converted_ride['geojson_filename'] = geojson_filename

    return merged_and_converted_ride







    







