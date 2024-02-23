"""
This module provides functions downloading bus locations data.
"""

from secrets import API_KEY

from time import sleep
from datetime import datetime

from utils import save_data, send_request


def get_available_buses():
    """
    Downloads bus locations from ZTM API.

    Returns:
    - json: response from the server.  
    """
    url = ("https://api.um.warszawa.pl/api/action/busestrams_get/?"
           f"resource_id= f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey={API_KEY}&type=1")

    return send_request(url)

def download_data(data_dir):
    """
    Downloads bus locations data to data_dir measured from a 1h time window.
    """
    acc_results = []

    download_time = datetime.now()

    try:
        for _ in range(60):
            results = get_available_buses()
            if results is None:
                continue
            results = results.json()['result']
            print(f"downloaded data ({datetime.now()})")
            acc_results.extend(results)
            sleep(60)
    except KeyboardInterrupt:
        print("downloading interrupted")

    save_data(acc_results, data_dir, f"bus-locations-{download_time}.json")

    print("downloading finished")
