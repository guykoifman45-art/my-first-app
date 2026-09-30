import requests
import json
import sys
import datetime

def fetch_weather(location: str) -> dict:
    try:
        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid=your_api_key')
        response.raise_for_status()
        data = response.json()
        return {
            'location': data['name'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'timestamp': datetime.datetime.now().isoformat()
        }
    except requests.RequestException as e:
        raise e
    except ValueError as e:
        raise ValueError("Invalid JSON response")

def save_to_json(data: dict, filename: str) -> None:
    if data is None:
        raise ValueError("Data cannot be None")
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
    except (TypeError, ValueError) as e:
        raise ValueError("Data is not JSON-serializable")
    except IOError as e:
        raise IOError("File write failure")

if __name__ == "__main__":
    try:
        result = fetch_weather('Tokyo')
        save_to_json(result, 'weather.json')
        sys.exit(0)
    except requests.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
