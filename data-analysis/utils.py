import json
from datetime import datetime
from geopy.distance import geodesic

def get_coords(bus):
    return (bus['Lat'], bus['Lon'])

def get_time(bus):
    return bus['Time']

def calculate_distance(coord1, coord2):
    return abs(geodesic(coord1, coord2).meters)

def calculate_speed(bus_data1, bus_data2):
    distance_m = calculate_distance(get_coords(bus_data1), get_coords(bus_data2))
    time_s = (get_time(bus_data2) - get_time(bus_data1)).total_seconds()
    if time_s == 0.0:
        return None
    speed_mps = distance_m / time_s
    speed_kmph = speed_mps * 3.6
    return speed_kmph

def validate_time_format(time_str):
    try:
        datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return True
    except:
        return False