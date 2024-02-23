"""
This module provides scripts for analysis of punctuality.
"""

import os
import json
from datetime import datetime, timedelta
from tqdm import tqdm

from utils import get_time, get_coords, validate_datetime_format,\
                  validate_time_format, is_at_stop, BUS_DATA_MEASUREMENT_TIME


def get_buses_data(filepath):
    """
    Reads buses data from filepath.
    """
    with open(filepath, "r", encoding="utf-8") as json_file:
        buses_data = json.load(json_file)

    return buses_data

def get_schedules(data_dir):
    """
    Reads schedules data from data_dir/bus_schedules.json.
    """
    filepath_schedules = os.path.join(data_dir, "bus-schedules.json")

    with open(filepath_schedules, "r", encoding="utf-8") as json_file:
        schedules_data = json.load(json_file)

    return schedules_data

def get_bus_stops_locations(data_dir):
    """
    Reads bus stops locations from data_dir/bus-stops.json.    
    """
    filepath_bus_stops = os.path.join(data_dir, "bus-stops.json")

    with open(filepath_bus_stops, "r", encoding="utf-8") as json_file:
        bus_stops_data = json.load(json_file)

    bus_stops_to_locations = {(bus_stop["values"][0]["value"], bus_stop["values"][1]["value"]):
                              (bus_stop["values"][4]["value"], bus_stop["values"][5]["value"])
                              for bus_stop in bus_stops_data["result"]}

    return bus_stops_to_locations

def get_bus_locations(buses_data, download_time):
    """
    Gets bus lines locations based on live bus data.
    """
    buses = [bus["VehicleNumber"] for bus in buses_data
             if isinstance(bus, dict) and "VehicleNumber" in bus]
    bus_lines = [bus["Lines"] for bus in buses_data if isinstance(bus, dict) and "Lines" in bus]

    print(f"skipped {len(buses_data) - len(buses)} elements out of {len(buses_data)}")

    bus_lines = list(set(bus_lines))

    bus_locations = {bus_line: [] for bus_line in bus_lines}

    for data_point in buses_data:
        if not isinstance(data_point, dict) or not validate_datetime_format(get_time(data_point)):
            continue
        time = datetime.strptime(data_point['Time'], '%Y-%m-%d %H:%M:%S')
        if time < download_time:
            continue
        bus_locations[data_point["Lines"]].append((time, (get_coords(data_point))))

    for bus_line in bus_locations:
        bus_locations[bus_line] = sorted(bus_locations[bus_line], key=lambda x: x[0])


    return bus_locations

def calculate_delays(data_dir, filepath, download_time):
    """
    Calculates delays for buses and returns those that exceeded 2 minutes.
    """
    buses_data = get_buses_data(filepath)
    schedules_data = get_schedules(data_dir)
    bus_stops_to_locations = get_bus_stops_locations(data_dir)
    bus_locations = get_bus_locations(buses_data, download_time)

    delayed_buses = []
    bus_lines_not_found = []
    not_arrived = 0

    for sid in tqdm(schedules_data):
        bus_stop_id, bus_stop_nr, bus_line = sid.split(',')

        times = schedules_data[sid]
        times = [datetime.strptime(time, '%H:%M:%S').time()
                for time in times if validate_time_format(time)]
        times = [download_time.replace(
            hour=t.hour, minute=t.minute, second=t.second) for t in times]
        times = [time for time in times if download_time <=
                time <= download_time + BUS_DATA_MEASUREMENT_TIME]

        bus_stop_loc = bus_stops_to_locations[(bus_stop_id, bus_stop_nr)]

        try:
            locations = bus_locations[bus_line]
        except KeyError:
            bus_lines_not_found.append(bus_line)
            continue

        for time in times:
            arrival = next(((t, bus_loc) for (t, bus_loc) in locations if t >= time -
                        timedelta(minutes=2) and is_at_stop(bus_loc, bus_stop_loc)), None)

            if arrival is None:
                not_arrived += 1
                continue

            delay = arrival[0] - time
            if delay >= timedelta(minutes=2):
                delayed_buses.append((bus_line, bus_stop_id, time, delay))

    print(f"bus lines not found in live data: {len(set(bus_lines_not_found))},\
           buses that did not arrive: {not_arrived}")

    return delayed_buses
