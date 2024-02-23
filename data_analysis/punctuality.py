import json
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm

from utils import get_time, get_coords, validate_datetime_format, validate_time_format, is_at_stop, BUS_DATA_MEASUREMENT_TIME


filepath_morning = "../data/bus-locations-2024-02-19 09:35:12.222315.json"
filepath_evening = "../data/bus-locations-2024-02-18 20:29:31.691732.json"

timestamp_morning = datetime.strptime("2024-02-19 09:35:12", '%Y-%m-%d %H:%M:%S')
timestamp_evening = datetime.strptime("2024-02-18 20:29:31", '%Y-%m-%d %H:%M:%S')
download_time = timestamp_morning


def get_buses_data(filepath):
    with open(filepath, "r", encoding="utf-8") as json_file:
        buses_data = json.load(json_file)

    return buses_data

def get_schedules():
    filepath_schedules = "../data/bus-schedules.json"

    with open(filepath_schedules, "r", encoding="utf-8") as json_file:
            schedules_data = json.load(json_file)
        
    return schedules_data

def get_bus_stops_locations():
    filepath_bus_stops = "../data/bus-stops.json"

    with open(filepath_bus_stops, "r", encoding="utf-8") as json_file:
        bus_stops_data = json.load(json_file)

    bus_stops_to_locations = {(bus_stop["values"][0]["value"], bus_stop["values"][1]["value"]): (bus_stop["values"][4]["value"], bus_stop["values"][5]["value"]) for bus_stop in bus_stops_data["result"]}

    return bus_stops_to_locations

def get_bus_locations(buses_data):
    buses = [bus["VehicleNumber"] for bus in buses_data if isinstance(bus, dict) and "VehicleNumber" in bus]
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

def calculate_delays(filepath):
    buses_data = get_buses_data(filepath)
    schedules_data = get_schedules()    
    bus_stops_to_locations = get_bus_stops_locations()
    bus_locations = get_bus_locations(buses_data)

    delayed_buses = []
    bus_lines_not_found = []
    not_arrived = 0

    for id in tqdm(schedules_data):
        bus_stop_id, bus_stop_nr, bus_line = id.split(',')

        times = schedules_data[id]
        times = [datetime.strptime(time, '%H:%M:%S').time()
                for time in times if validate_time_format(time)]
        times = [download_time.replace(
            hour=t.hour, minute=t.minute, second=t.second) for t in times]
        times = [time for time in times if download_time <=
                time <= download_time + BUS_DATA_MEASUREMENT_TIME]

        bus_stop_loc = bus_stops_to_locations[(bus_stop_id, bus_stop_nr)]

        try:
            locations = bus_locations[bus_line]
        except KeyError as e:
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

def save_data(delayed_buses):
    filepath = f"delays.json"

    def datetime_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (list, dict)):
            return obj
        else:
            return str(obj)

    json_data = json.dumps(delayed_buses, default=datetime_serializer, indent=2)

    with open(filepath, "w") as json_file:
        json_file.write(json_data)


