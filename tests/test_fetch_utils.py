import os
import json
from unittest.mock import patch, MagicMock
import requests
import pytest
from requests.exceptions import ConnectionError, RequestException

from data_fetching.utils import send_request, save_data

@pytest.fixture
def mock_post_request_success():
    # Fixture for a successful post request
    mock_response = MagicMock()
    mock_response.status_code = 200
    return mock_response

@pytest.fixture
def mock_post_request_failure():
    # Fixture for a failing post request
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = RequestException("Mocked RequestException")
    return mock_response

def test_send_request_success(mock_post_request_success):
    # Mock the requests.post method to return a successful response
    with patch('requests.post', return_value=mock_post_request_success):
        url = "http://example.com"
        response = send_request(url)
        assert response.status_code == 200

def test_send_request_failure_retries(mock_post_request_failure, monkeypatch):
    # Mock the requests.post method to raise an exception (simulate failure)
    def mock_post(*args, **kwargs):
        raise ConnectionError("Mocked ConnectionError")

    monkeypatch.setattr(requests, 'post', mock_post)

    url = "http://example.com"
    response = send_request(url)

    # Ensure that the function returns None after 5 retries
    assert response is None

def test_save_data(tmpdir):
    # Test the save_data function
    data = {'key': 'value'}
    filename = 'test_data.json'
    data_dir = tmpdir.strpath  # Using a temporary directory

    filepath = os.path.join(data_dir, filename)

    # Call the function
    save_data(data, data_dir, filename)

    # Check if the file was created and contains the correct data
    assert os.path.isfile(filepath)

    with open(filepath, 'r') as json_file:
        loaded_data = json.load(json_file)

    assert loaded_data == data
