"""
Module with analysis utils
"""
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

BUS_DATA_MEASUREMENT_TIME = timedelta(hours=1)

EPS = 200.0

def haversine_distance(coord1, coord2):
    """
    Calculate the haversine distance between two coordinates.

    Parameters:
    - coord1 (tuple): A tuple containing latitude and longitude for the first point.
    - coord2 (tuple): A tuple containing latitude and longitude for the second point.

    Returns:
    - float: The distance in meters.
    """

    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    # Radius of the Earth in kilometers
    radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the differences between the coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a_var = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c_var = 2 * atan2(sqrt(a_var), sqrt(1 - a_var))

    # Distance in kilometers
    distance = radius * c_var

    return distance * 1000.0

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
    Calculate the distance between two coordinates.

    Parameters:
    - coord1 (tuple): A tuple containing latitude and longitude for the first point.
    - coord2 (tuple): A tuple containing latitude and longitude for the second point.

    Returns:
    - float: The distance in meters.
    """
    # return abs(geodesic(coord1, coord2).meters)
    return haversine_distance(coord1, coord2)

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

def validate_datetime_format(datetime_str):
    """
    Validate if the input datetime string is in the format '%Y-%m-%d %H:%M:%S'.

    Parameters:
    - time_str (str): A string representing a time in the specified format.

    Returns:
    - bool: True if the format is valid, False otherwise.
    """
    try:
        datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False

def validate_time_format(time_str):
    """
    Validate if the input time string is in the format '%H:%M:%S'.

    Parameters:
    - time_str (str): A string representing a time in the specified format.

    Returns:
    - bool: True if the format is valid, False otherwise.
    """
    try:
        datetime.strptime(time_str, '%H:%M:%S')
        return True
    except ValueError:
        return False

def is_at_stop(bus_loc, bus_stop_loc):
    """
    Check if the bus is at the bus stop.

    Parameters:
    - bus_loc (tuple[float, float]): Geographical coordinates of bus location
    - bus_stop_loc (tuple[float, float]): Geographical coordinates of bus stop location

    Returns:
    - bool: True if the bus is close to the bus stop, False otherwise.
    """
    return calculate_distance(bus_loc, bus_stop_loc) < EPS
