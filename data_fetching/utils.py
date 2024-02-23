"""
This module provides utilities for data fetching.
"""

import os
from time import sleep
import json
from socket import gaierror
import requests
from requests.exceptions import RequestException, ConnectionError

def send_request(url):
    """
    Sends an API request at given url and returns the response.
    Retries 5 times on failure. 
    If all tries didn't succeed, returns None
    """
    retries = 5
    for _ in range(retries):
        try:
            response = requests.post(url, timeout=60)
            response.raise_for_status()
            return response
        except ConnectionError as err:
            print(f"connection error, retrying in 3s... {err}")
            sleep(3)
        except gaierror as err:
            print(f"gaierror, retrying in 3s... {err}")
            sleep(3)
        except RequestException as err:
            print(f"request exception, retrying in 3s... {err}")
            sleep(3)

    return None

def save_data(data, data_dir, filename):
    """
    Saves data to data_dir/filename.
    """
    filepath = os.path.join(data_dir, filename)

    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2)
