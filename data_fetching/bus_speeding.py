import json
from time import sleep
from datetime import datetime
import requests

from secrets import API_KEY


def get_available_buses():
    url = f"https://api.um.warszawa.pl/api/action/busestrams_get/?\
        resource_id= f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey={API_KEY}&type=1"

    response = requests.post(url)

    return response

def download_data():
    acc_results = []

    download_time = datetime.now()

    for _ in range(60):
        try:
            results = get_available_buses().json()['result']
            print(f"downloaded data ({datetime.now()})")
        except:
            print("request failed, retrying...")
            sleep(1)
        acc_results.extend(results)
        sleep(60)

    print(len(acc_results))

    filepath = f"../data/bus-locations-{download_time}.json"
    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(acc_results, json_file, indent=2)

download_data()
