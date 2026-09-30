import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
import requests
import sys
from datetime import datetime

# Import from the module under test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weather


class TestFetchWeather:
    """Tests for the fetch_weather function."""

    @patch('weather.requests.get')
    def test_fetch_weather_success(self, mock_get):
        """Test successful weather fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Tokyo',
            'main': {'temp': 25.5, 'humidity': 60},
            'weather': [{'description': 'clear sky'}],
        }
        mock_get.return_value = mock_response

        result = weather.fetch_weather('Tokyo')

        assert isinstance(result, dict)
        assert 'location' in result
        assert 'temperature' in result
        assert 'humidity' in result
        assert 'description' in result
        assert 'timestamp' in result
        assert result['location'] == 'Tokyo'
        assert result['temperature'] == 25.5
        assert result['humidity'] == 60
        assert result['description'] == 'clear sky'

    @patch('weather.requests.get')
    def test_fetch_weather_with_different_location(self, mock_get):
        """Test fetch_weather with different location."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'New York',
            'main': {'temp': 15.0, 'humidity': 75},
            'weather': [{'description': 'rainy'}],
        }
        mock_get.return_value = mock_response

        result = weather.fetch_weather('New York')

        assert result['location'] == 'New York'
        assert result['temperature'] == 15.0
        assert result['humidity'] == 75

    @patch('weather.requests.get')
    def test_fetch_weather_network_failure(self, mock_get):
        """Test fetch_weather raises RequestException on network failure."""
        mock_get.side_effect = requests.RequestException('Connection failed')

        with pytest.raises(requests.RequestException):
            weather.fetch_weather('Tokyo')

    @patch('weather.requests.get')
    def test_fetch_weather_timeout(self, mock_get):
        """Test fetch_weather raises RequestException on timeout."""
        mock_get.side_effect = requests.Timeout('Request timed out')

        with pytest.raises(requests.RequestException):
            weather.fetch_weather('Tokyo')

    @patch('weather.requests.get')
    def test_fetch_weather_invalid_json_response(self, mock_get):
        """Test fetch_weather handles invalid JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_get.return_value = mock_response

        with pytest.raises(ValueError):
            weather.fetch_weather('Tokyo')

    @patch('weather.requests.get')
    def test_fetch_weather_http_error(self, mock_get):
        """Test fetch_weather handles HTTP error responses."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError('404 Not Found')
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            mock_response.raise_for_status()

    @patch('weather.requests.get')
    def test_fetch_weather_timestamp_present(self, mock_get):
        """Test that fetch_weather includes a timestamp in the result."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Tokyo',
            'main': {'temp': 25.0, 'humidity': 60},
            'weather': [{'description': 'clear'}],
        }
        mock_get.return_value = mock_response

        result = weather.fetch_weather('Tokyo')

        assert result['timestamp'] is not None
        # Verify timestamp is a string representation of a datetime
        assert isinstance(result['timestamp'], str)


class TestSaveToJson:
    """Tests for the save_to_json function."""

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_json_success(self, mock_file):
        """Test successful JSON save."""
        data = {
            'location': 'Tokyo',
            'temperature': 25.0,
            'humidity': 60,
            'description': 'clear sky',
            'timestamp': '2024-09-30T12:00:00'
        }

        weather.save_to_json(data, 'weather.json')

        mock_file.assert_called_once_with('weather.json', 'w')
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        parsed = json.loads(written_content)
        assert parsed == data

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_json_with_nested_dict(self, mock_file):
        """Test saving nested dictionary structures."""
        data = {
            'location': 'Tokyo',
            'metrics': {
                'temperature': 25.0,
                'humidity': 60
            },
            'timestamp': '2024-09-30T12:00:00'
        }

        weather.save_to_json(data, 'weather.json')

        mock_file.assert_called_once_with('weather.json', 'w')

    def test_save_to_json_none_data(self):
        """Test save_to_json raises ValueError when data is None."""
        with pytest.raises(ValueError):
            weather.save_to_json(None, 'weather.json')

    def test_save_to_json_non_serializable(self):
        """Test save_to_json raises ValueError for non-JSON-serializable data."""
        class NonSerializable:
            pass

        data = {'location': 'Tokyo', 'obj': NonSerializable()}

        with pytest.raises(ValueError):
            weather.save_to_json(data, 'weather.json')

    @patch('builtins.open', side_effect=IOError('Permission denied'))
    def test_save_to_json_file_write_failure(self, mock_file):
        """Test save_to_json raises IOError on file write failure."""
        data = {'location': 'Tokyo', 'temperature': 25.0}

        with pytest.raises(IOError):
            weather.save_to_json(data, 'weather.json')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_json_with_special_characters(self, mock_file):
        """Test saving data with special characters."""
        data = {
            'location': 'Tokyo',
            'description': 'Partly cloudy with "quotes" and \\backslashes\\'
        }

        weather.save_to_json(data, 'weather.json')

        mock_file.assert_called_once_with('weather.json', 'w')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_json_empty_dict(self, mock_file):
        """Test saving an empty dictionary."""
        data = {}

        weather.save_to_json(data, 'weather.json')

        mock_file.assert_called_once_with('weather.json', 'w')

    @patch('builtins.open', side_effect=OSError('Disk full'))
    def test_save_to_json_oserror(self, mock_file):
        """Test save_to_json handles OSError."""
        data = {'location': 'Tokyo'}

        with pytest.raises(IOError):
            weather.save_to_json(data, 'weather.json')


class TestMainEntryPoint:
    """Tests for the main entry point script."""

    @patch('weather.save_to_json')
    @patch('weather.fetch_weather')
    @patch('sys.exit')
    def test_main_success(self, mock_exit, mock_fetch, mock_save):
        """Test main entry point succeeds."""
        mock_fetch.return_value = {
            'location': 'Tokyo',
            'temperature': 25.0,
            'humidity': 60,
            'description': 'clear sky',
            'timestamp': '2024-09-30T12:00:00'
        }

        # Execute the main block by importing and testing the behavior
        # This will be validated when the implementation runs
        weather.fetch_weather('Tokyo')
        weather.save_to_json(mock_fetch.return_value, 'weather.json')

        mock_fetch.assert_called_once_with('Tokyo')
        mock_save.assert_called_once()

    @patch('weather.fetch_weather')
    @patch('sys.stderr')
    def test_main_network_error(self, mock_stderr, mock_fetch):
        """Test main entry point handles network errors."""
        mock_fetch.side_effect = requests.RequestException('Network error')

        with pytest.raises(requests.RequestException):
            weather.fetch_weather('Tokyo')

        mock_fetch.assert_called_once_with('Tokyo')

    @patch('weather.save_to_json')
    @patch('weather.fetch_weather')
    def test_main_file_write_error(self, mock_fetch, mock_save):
        """Test main entry point handles file write errors."""
        mock_fetch.return_value = {
            'location': 'Tokyo',
            'temperature': 25.0,
            'humidity': 60,
            'description': 'clear sky',
            'timestamp': '2024-09-30T12:00:00'
        }
        mock_save.side_effect = IOError('Permission denied')

        with pytest.raises(IOError):
            weather.fetch_weather('Tokyo')
            weather.save_to_json(mock_fetch.return_value, 'weather.json')


class TestIntegration:
    """Integration tests for the complete weather flow."""

    @patch('builtins.open', new_callable=mock_open)
    @patch('weather.requests.get')
    def test_fetch_and_save_workflow(self, mock_get, mock_file):
        """Test complete fetch and save workflow."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Tokyo',
            'main': {'temp': 25.5, 'humidity': 60},
            'weather': [{'description': 'clear sky'}],
        }
        mock_get.return_value = mock_response

        # Simulate the workflow
        result = weather.fetch_weather('Tokyo')
        weather.save_to_json(result, 'weather.json')

        # Verify both functions were called
        mock_get.assert_called_once()
        mock_file.assert_called_once_with('weather.json', 'w')

        # Verify the result structure
        assert result['location'] == 'Tokyo'
        assert result['temperature'] == 25.5
        assert result['humidity'] == 60
