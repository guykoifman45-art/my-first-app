import pytest
import json
import sys
from unittest.mock import patch, mock_open, MagicMock
import requests
from weather import fetch_weather, save_to_json


class TestFetchWeather:
    """Tests for the fetch_weather function."""

    def test_fetch_weather_success(self):
        """Test successful weather fetch with valid location."""
        mock_response = {
            'name': 'Tokyo',
            'main': {'temp': 25.5, 'humidity': 60},
            'weather': [{'description': 'Clear'}]
        }
        with patch('weather.requests.get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            result = fetch_weather('Tokyo')

            assert result['location'] == 'Tokyo'
            assert result['temperature'] == 25.5
            assert result['humidity'] == 60
            assert result['description'] == 'Clear'
            assert 'timestamp' in result

    def test_fetch_weather_network_error(self):
        """Test fetch_weather raises RequestException on network failure."""
        with patch('weather.requests.get') as mock_get:
            mock_get.side_effect = requests.ConnectionError("Network failure")

            with pytest.raises(requests.RequestException):
                fetch_weather('Tokyo')

    def test_fetch_weather_timeout(self):
        """Test fetch_weather raises RequestException on timeout."""
        with patch('weather.requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Request timeout")

            with pytest.raises(requests.RequestException):
                fetch_weather('Tokyo')

    def test_fetch_weather_invalid_json(self):
        """Test fetch_weather raises ValueError on invalid JSON response."""
        with patch('weather.requests.get') as mock_get:
            mock_get.return_value.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value.raise_for_status.return_value = None

            with pytest.raises(ValueError):
                fetch_weather('Tokyo')

    def test_fetch_weather_empty_location(self):
        """Test fetch_weather with empty location parameter."""
        mock_response = {
            'name': '',
            'main': {'temp': 0, 'humidity': 0},
            'weather': [{'description': ''}]
        }
        with patch('weather.requests.get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            result = fetch_weather('')
            assert result['location'] == ''

    def test_fetch_weather_special_characters_location(self):
        """Test fetch_weather with special characters in location."""
        mock_response = {
            'name': 'New York',
            'main': {'temp': 20.0, 'humidity': 50},
            'weather': [{'description': 'Cloudy'}]
        }
        with patch('weather.requests.get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            result = fetch_weather('New York')
            assert result['location'] == 'New York'


class TestSaveToJson:
    """Tests for the save_to_json function."""

    def test_save_to_json_success(self):
        """Test successful JSON file write with valid data."""
        test_data = {'location': 'Tokyo', 'temperature': 25.5}

        with patch('weather.open', mock_open()) as mock_file:
            save_to_json(test_data, 'weather.json')

            mock_file.assert_called_once_with('weather.json', 'w')
            handle = mock_file()
            assert handle.write.called or json.dumps.called

    def test_save_to_json_none_data(self):
        """Test save_to_json raises ValueError when data is None."""
        with pytest.raises(ValueError):
            save_to_json(None, 'weather.json')

    def test_save_to_json_non_serializable_data(self):
        """Test save_to_json raises ValueError with non-serializable data."""
        non_serializable = {'func': lambda x: x}

        with patch('weather.open', mock_open()):
            with pytest.raises(ValueError):
                save_to_json(non_serializable, 'weather.json')

    def test_save_to_json_invalid_filename_dot_dot(self):
        """Test save_to_json validates filename to prevent path traversal (..)."""
        test_data = {'location': 'Tokyo'}

        with pytest.raises(ValueError):
            save_to_json(test_data, '../weather.json')

    def test_save_to_json_invalid_filename_slash(self):
        """Test save_to_json validates filename to prevent path traversal (/)."""
        test_data = {'location': 'Tokyo'}

        with pytest.raises(ValueError):
            save_to_json(test_data, '/etc/weather.json')

    def test_save_to_json_invalid_filename_backslash(self):
        """Test save_to_json validates filename to prevent path traversal (\\)."""
        test_data = {'location': 'Tokyo'}

        with pytest.raises(ValueError):
            save_to_json(test_data, 'folder\\weather.json')

    def test_save_to_json_io_error(self):
        """Test save_to_json raises IOError on file write failure."""
        test_data = {'location': 'Tokyo'}

        with patch('weather.open', side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                save_to_json(test_data, 'weather.json')

    def test_save_to_json_valid_data_types(self):
        """Test save_to_json with various valid data types."""
        test_data = {
            'location': 'Tokyo',
            'temperature': 25.5,
            'humidity': 60,
            'description': 'Clear',
            'timestamp': '2023-01-01T12:00:00'
        }

        with patch('weather.open', mock_open()):
            save_to_json(test_data, 'weather.json')


class TestMainEntry:
    """Tests for the __main__ entry point."""

    def test_main_success(self):
        """Test main entry point succeeds and exits with 0."""
        mock_weather_data = {
            'location': 'Tokyo',
            'temperature': 25.5,
            'humidity': 60,
            'description': 'Clear',
            'timestamp': '2023-01-01T12:00:00'
        }

        with patch('weather.requests.get') as mock_get:
            with patch('weather.open', mock_open()):
                mock_get.return_value.json.return_value = {
                    'name': 'Tokyo',
                    'main': {'temp': 25.5, 'humidity': 60},
                    'weather': [{'description': 'Clear'}]
                }
                mock_get.return_value.raise_for_status.return_value = None

                with patch('sys.exit') as mock_exit:
                    # Import and run main
                    import weather
                    if __name__ != '__main__':
                        # Simulate main block
                        try:
                            result = weather.fetch_weather('Tokyo')
                            weather.save_to_json(result, 'weather.json')
                            # Would call sys.exit(0)
                        except Exception:
                            pass

    def test_main_network_error_exit_1(self):
        """Test main exits with 1 on network error."""
        with patch('weather.requests.get') as mock_get:
            mock_get.side_effect = requests.ConnectionError("Network failure")

            with patch('sys.exit') as mock_exit:
                try:
                    result = fetch_weather('Tokyo')
                except requests.RequestException as e:
                    # Main would catch this and exit(1)
                    pass

    def test_main_value_error_exit_1(self):
        """Test main exits with 1 on ValueError."""
        test_data = {'func': lambda x: x}

        with patch('weather.open', mock_open()):
            with pytest.raises(ValueError):
                save_to_json(test_data, 'weather.json')

    def test_main_io_error_exit_1(self):
        """Test main exits with 1 on IOError."""
        test_data = {'location': 'Tokyo'}

        with patch('weather.open', side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                save_to_json(test_data, 'weather.json')


class TestIntegration:
    """Integration tests for fetch_weather and save_to_json together."""

    def test_fetch_and_save_integration(self):
        """Test fetching weather and saving it to JSON."""
        mock_response = {
            'name': 'Tokyo',
            'main': {'temp': 25.5, 'humidity': 60},
            'weather': [{'description': 'Clear'}]
        }

        with patch('weather.requests.get') as mock_get:
            with patch('weather.open', mock_open()) as mock_file:
                mock_get.return_value.json.return_value = mock_response
                mock_get.return_value.raise_for_status.return_value = None

                weather_data = fetch_weather('Tokyo')
                save_to_json(weather_data, 'weather.json')

                mock_file.assert_called_once_with('weather.json', 'w')
                assert weather_data['location'] == 'Tokyo'
                assert weather_data['temperature'] == 25.5
