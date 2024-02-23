import datetime
from unittest.mock import MagicMock
import pytest
from data_analysis.utils import (
    haversine_distance,
    get_coords,
    get_time,
    calculate_distance,
    calculate_speed,
    validate_datetime_format,
    validate_time_format,
    is_at_stop,
)

EPS = 1e-6  # A small epsilon for floating-point comparisons

# Define a fixture for bus data
@pytest.fixture
def bus_data():
    return {
        'Lat': 52.5200,
        'Lon': 13.4050,
        'Time': datetime.datetime(2024, 2, 18, 12, 0, 0),
    }

def test_haversine_distance():
    coord1 = (52.5200, 13.4050)
    coord2 = (52.5200, 13.4050)
    distance = haversine_distance(coord1, coord2)
    assert distance == pytest.approx(0, EPS)  # Approximate square root of 2 times 1000

def test_get_coords(bus_data):
    coords = get_coords(bus_data)
    assert coords == (52.5200, 13.4050)

def test_get_time(bus_data):
    time = get_time(bus_data)
    assert time == datetime.datetime(2024, 2, 18, 12, 0, 0)

def test_calculate_distance():
    coord1 = (52.5200, 13.4050)
    coord2 = (52.5200, 13.4050)
    distance = calculate_distance(coord1, coord2)
    assert distance == pytest.approx(0, EPS)

def test_calculate_speed(bus_data):
    bus_data2 = {
        'Lat': 52.5200,
        'Lon': 13.4050,
        'Time': datetime.datetime(2024, 2, 18, 12, 5, 0),
    }
    speed = calculate_speed(bus_data, bus_data2)
    assert speed == pytest.approx(0, EPS)  # Approximate speed in km/h

def test_validate_datetime_format():
    assert validate_datetime_format('2024-02-18 12:00:00')
    assert not validate_datetime_format('2024-02-18 12:00')  # Missing seconds
    assert not validate_datetime_format('2024-02-18T12:00:00')  # Incorrect format

def test_validate_time_format():
    assert validate_time_format('12:00:00')
    assert not validate_time_format('12:00')  # Missing seconds
    assert not validate_time_format('12:00:00 AM')  # Incorrect format

def test_is_at_stop():
    bus_loc = (52.5200, 13.4050)
    bus_stop_loc = (52.5200, 13.4050)
    assert is_at_stop(bus_loc, bus_stop_loc)
    assert not is_at_stop(bus_loc, (52.5400, 13.4200))  # Bus is not close enough