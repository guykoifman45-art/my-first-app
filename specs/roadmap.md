# Roadmap

## Milestone 1: Foundational Setup

- `my-first-app/requirements.txt` — dependency manifest with requests, pytest, pytest-cov, black, flake8

## Milestone 2: Core Weather Fetching

- `my-first-app/weather.py` — main script with (1) `fetch_weather(location)` function that calls an external API (or returns mock data), (2) `save_to_json(data, filename)` function that serializes and writes JSON to file, (3) `__main__` block that orchestrates the flow for Tokyo

## Milestone 3: Comprehensive Test Coverage

- `my-first-app/test_weather.py` — unit tests covering (1) successful weather fetch and JSON save, (2) network failure handling via mocked API exception, (3) invalid input validation, (4) JSON serialization edge cases, (5) file write error handling

## Deferred

- Real external API integration (currently mocked for testability)
- Weather data caching or database storage
- Multi-location support
- CLI argument parsing for location/output filename
- Scheduled execution or cron integration
