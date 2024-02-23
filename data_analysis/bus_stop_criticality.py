"""
This module provides scripts for analysis of bus stop criticality.
"""

import os
import json

import folium


def calculate_bus_stop_criticality(data_dir):
    """
    Calculates bus stops criticallity 
    and returns dictionary with the results.
    """
    filepath = os.path.join(data_dir, "bus-schedules.json")

    with open(filepath, "r", encoding="utf-8") as json_file:
        bus_schedules = json.load(json_file)

    count_scheduled_stops = {}

    for sid in bus_schedules:
        bus_stop_id, bus_stop_nr, _ = sid.split(',')
        stops = bus_schedules[sid]
        if (bus_stop_id, bus_stop_nr) not in count_scheduled_stops:
            count_scheduled_stops[(bus_stop_id, bus_stop_nr)] = 0
        count_scheduled_stops[(bus_stop_id, bus_stop_nr)] += len(stops)

    return count_scheduled_stops


def generate_criticality_map(data_frame):
    """
    Generate a Folium map with latitude and longitude points, where the color temperature
    is proportional to .

    Parameters:
    - df (pandas.DataFrame): DataFrame with Latitude and Longitude points of bus stops
    with values proportional to criticality of the bus stop. 

    Returns:
    - folium.Map: A Folium map object.
    """
    warsaw_map = folium.Map(location=[52.2298, 21.0118], zoom_start=12)

    colormap = folium.LinearColormap(colors=["blue", "green", "yellow", "red"],
                                     vmin=data_frame["Number of scheduled stops"].min(),
                                     vmax=data_frame["Number of scheduled stops"].max())

    for _, row in data_frame.iterrows():
        folium.Marker(
            location=[row['Latitude'], row["Longitude"]],
            popup=f"Number of scheduled stops: {row['Number of scheduled stops']}",
            icon=folium.Icon(color=colormap(row["Number of scheduled stops"]), icon='info-sign')
        ).add_to(warsaw_map)


    return warsaw_map
