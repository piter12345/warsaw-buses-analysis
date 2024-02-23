"""
This module provides functions downloading bus schedules data.
"""

from secrets import API_KEY

from datetime import datetime
from tqdm import tqdm

from utils import save_data, send_request


def get_bus_lines_stopping(bus_stop_id, bus_stop_nr):
    """
    Downloads bus lines that are stopping on a bus stop specified 
    by parameters bus_stop_id, bus_stop_nr.
    """
    url = ("https://api.um.warszawa.pl/api/action/dbtimetable_get?"
           "id=88cd555f-6f31-43ca-9de4-66c479ad5942&"
           f"busstopId={bus_stop_id}&busstopNr={bus_stop_nr}&apikey={API_KEY}")

    return send_request(url)

def get_bus_stops():
    """
    Downloads list of bus stops.
    """
    url = ("https://api.um.warszawa.pl/api/action/dbstore_get?"
           f"id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&apikey={API_KEY}")

    return send_request(url)

def get_bus_schedule(bus_stop_id, bus_stop_nr, bus_line):
    """
    Downloads schedule for given bus stop and given bus line.
    """
    url = ("https://api.um.warszawa.pl/api/action/dbtimetable_get/?"
           "id=e923fa0e-d96c-43f9-ae6e-60518c9f3238"
           f"&busstopId={bus_stop_id}&busstopNr={bus_stop_nr}&line={bus_line}&apikey={API_KEY}")

    return send_request(url)


def download_data(data_dir):
    """
    Downloads bus schedules data and saves it to data_dir.
    """
    download_time = datetime.now()

    data = get_bus_stops().json()

    save_data(data, data_dir, f"bus-stops-{download_time}.json")

    bus_stop_ids = [value["values"][0]["value"] for value in data["result"]]
    bus_stop_nrs = [value["values"][1]["value"] for value in data["result"]]

    bus_stop_to_bus_lines_stopping = {}
    try:
        for bus_stop_id, bus_stop_nr in tqdm(zip(bus_stop_ids, bus_stop_nrs),
                                             desc="Downloading bus lines stopping",
                                             unit=" iterations",
                                             total=len(bus_stop_ids)):
            result = get_bus_lines_stopping(bus_stop_id, bus_stop_nr).json()
            bus_lines_stopping = [kv["values"][0]["value"] for kv in result["result"]]
            bus_stop_to_bus_lines_stopping[(bus_stop_id, bus_stop_nr)] = bus_lines_stopping
    except KeyboardInterrupt:
        print("downloading interrupted")

    data = {f"{id},{nr}": bus_stop_to_bus_lines_stopping[(id, nr)]
            for id, nr in bus_stop_to_bus_lines_stopping}

    save_data(data, data_dir, f"bus-stops-to-bus-lines-{download_time}.json")

    bus_schedules = {}
    try:
        for key in tqdm(data,
                        desc="Downloading bus schedules"):
            bus_stop_id, bus_stop_nr = key.split(',')
            for bus_line in data[key]:
                response = get_bus_schedule(bus_stop_id, bus_stop_nr, bus_line)
                stops = response.json()["result"]
                times = [stop["values"][-1]["value"] for stop in stops]
                bus_schedules[f"{bus_stop_id},{bus_stop_nr},{bus_line}"] = times
    except KeyboardInterrupt:
        print("downloading interrupted")

    save_data(bus_schedules, data_dir, f"bus-schedules-{download_time}.json")
    print("downloading finished")
