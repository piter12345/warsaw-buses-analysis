"""
Module with analysis utils
"""
from datetime import datetime
from geopy.distance import geodesic

def get_coords(bus):
    """
    Get the coordinates (latitude and longitude) from the bus data.

    Parameters:
    - bus (dict): A dictionary representing bus data.

    Returns:
    - tuple: A tuple containing latitude and longitude.
    """
    return (bus['Lat'], bus['Lon'])

def get_time(bus):
    """
    Get the time from the bus data.

    Parameters:
    - bus (dict): A dictionary representing bus data.

    Returns:
    - datetime: A datetime object representing the time.
    """
    return bus['Time']

def calculate_distance(coord1, coord2):
    """
    Calculate the distance between two coordinates using geodesic distance.

    Parameters:
    - coord1 (tuple): A tuple containing latitude and longitude for the first point.
    - coord2 (tuple): A tuple containing latitude and longitude for the second point.

    Returns:
    - float: The distance in meters.
    """
    return abs(geodesic(coord1, coord2).meters)

def calculate_speed(bus_data1, bus_data2):
    """
    Calculate the speed between two sets of bus data.

    Parameters:
    - bus_data1 (dict): A dictionary representing the first set of bus data.
    - bus_data2 (dict): A dictionary representing the second set of bus data.

    Returns:
    - float or None: The speed in kilometers per hour, or None if time difference is zero.
    """
    distance_m = calculate_distance(get_coords(bus_data1), get_coords(bus_data2))
    time_s = (get_time(bus_data2) - get_time(bus_data1)).total_seconds()
    if time_s == 0.0:
        return None
    speed_mps = distance_m / time_s
    speed_kmph = speed_mps * 3.6
    return speed_kmph

def validate_time_format(time_str):
    """
    Validate if the input time string is in the format '%Y-%m-%d %H:%M:%S'.

    Parameters:
    - time_str (str): A string representing a time in the specified format.

    Returns:
    - bool: True if the format is valid, False otherwise.
    """
    try:
        datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False
