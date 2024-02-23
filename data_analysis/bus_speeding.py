"""
This script processes JSON data related to buses, 
calculates speeds, and generates a map highlighting speeding buses.
"""

import json
from datetime import datetime

import folium
from folium.plugins import HeatMap

from utils import calculate_speed, validate_datetime_format


SPEED_LIMIT = 50.0


def parse_data(filepath):
    """
    Parse JSON data from a file, filter out invalid entries, and organize it by vehicle number.

    Parameters:
    - filepath (str): The path to the JSON file containing bus data.

    Returns:
    - dict: A dictionary mapping vehicle numbers to sorted lists of corresponding bus data.
    """
    with open(filepath, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    buses_list = [bus_data for bus_data in data
                  if isinstance(bus_data, dict) and validate_datetime_format(bus_data['Time'])]

    print(f"skipped {len(data) - len(buses_list)} elements out of {len(data)}")

    bus_to_data = {}
    for bus_data in buses_list:
        vehicle_number = bus_data.get('VehicleNumber')
        bus_data['Time'] = datetime.strptime(bus_data['Time'], '%Y-%m-%d %H:%M:%S')
        if vehicle_number in bus_to_data:
            bus_to_data[vehicle_number].append(bus_data)
        else:
            bus_to_data[vehicle_number] = [bus_data]

    for bus in bus_to_data:
        bus_to_data[bus] = sorted(bus_to_data[bus], key=lambda x: x['Time'])

    return bus_to_data


def get_speeding_buses(bus_to_data):
    """
    Identify buses that have exceeded the defined speed limit.

    Parameters:
    - bus_to_data (dict): A dictionary mapping vehicle numbers to lists of corresponding bus data.

    Returns:
    - list: A list of bus data points representing instances where the speed limit was exceeded.
    """
    count_buses_speeding = 0
    buses_speeding = []

    for bus in bus_to_data:
        bus_data = bus_to_data[bus]

        bus_data[0]['Speed'] = 0.0
        speed_limit_exceeded = False
        for i, (pt1, pt2) in enumerate(zip(bus_data[:-1], bus_data[1:])):
            speed = calculate_speed(pt1, pt2)
            bus_data[i + 1]['Speed'] = speed
            if speed is not None and speed > SPEED_LIMIT:
                speed_limit_exceeded = True
                buses_speeding.append(pt1)
        if speed_limit_exceeded:
            count_buses_speeding += 1
    print(f"found {count_buses_speeding} buses that exceeded \
          speed limit out of {len(bus_to_data)} buses")

    return buses_speeding


def generate_map(points):
    """
    Generate a Folium map with a heatmap overlay based on provided latitude and longitude points.

    Parameters:
    - points (list): A list of dictionaries representing latitude and longitude points.

    Returns:
    - folium.Map: A Folium map object.
    """
    warsaw_map = folium.Map(location=[52.2298, 21.0118], zoom_start=12)

    heat_data = [[point["Lat"], point["Lon"]] for point in points]
    HeatMap(heat_data).add_to(warsaw_map)

    return warsaw_map
