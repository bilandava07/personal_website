from zoneinfo import ZoneInfo
from datetime import datetime
from fitparse import FitFile



fitfile = FitFile('rides_fit/2025-09-12-160814-ELEMNT ROAM B53E-57-0.fit')

# Parses the .fit file and returns a readable json with name and values of the fit fiels

for session in fitfile.get_messages('session'):
    ride_data = {}
    for field in session:
        ride_data[field.name] = field.value

print(ride_data)

# Ask user for name and confirmation

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


avg_speed = ride_data['avg_speed']
max_speed = ride_data['max_speed']

distance = ride_data['total_distance']

total_time_s = ride_data['total_elapsed_time']
moving_time = ride_data['total_timer_time']

total_ascent = ride_data['total_ascent']
total_descent = ride_data['total_descent']

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



# Converts the parsed data to the right format
# e.g. speed is parsed in m/s ==> convert to km/h and round to one decimal place

avg_speed_kmh = round(ride_data['avg_speed'] * 3.6, 1)
max_speed_kmh = round(ride_data['max_speed'] * 3.6, 1)
distance_km = round(ride_data['total_distance'] / 1000, 1)

# convert time from seconds to respective formats

total_time_hr = round(ride_data['total_elapsed_time'] / 3600)
total_time_min = round((ride_data['total_elapsed_time'] % 3600) / 60)

total_time_formatted = f"{total_time_hr} h {total_time_min} m"

moving_time_hr = round(ride_data['total_timer_time'] / 3600)
moving_time_m = round((ride_data['total_timer_time'] % 3600) / 60)

moving_time_formatted = f"{moving_time_hr} h {moving_time_m} m"


start_time_utc = ride_data['start_time']

start_time_utc = start_time_utc.replace(tzinfo=ZoneInfo("UTC"))
# Convert to local timezone
local_tz = ZoneInfo("Europe/Berlin")  # change to your timezone
start_time_local = start_time_utc.astimezone(local_tz)



# Display format 
start_date_time = start_time_local.strftime("%d %B %Y at %H:%M")




moving_time_hr = ride_data['total_timer_time'] / 3600
paused_time_min = round((ride_data['total_elapsed_time'] - ride_data['total_timer_time']) / 60)

total_ascent = ride_data['total_ascent']
total_descent = ride_data['total_descent']




# print(f"Avg speed: {avg_speed_kmh} km/h")
# print(f"Max speed: {max_speed_kmh} km/h")
# print(f"Distance: {distance_km} km")
# print(f"Total time: {total_time_formatted}")
# print(f"Moving time: {moving_time_formatted} ")
# print(f"Paused time: {paused_time_min} min")
# print(f"Start: {start_date_time}")
# print(f"Total ascent: {total_ascent} m")
# print(f"Total descent: {total_descent} m")
