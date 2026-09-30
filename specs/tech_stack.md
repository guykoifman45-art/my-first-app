# Tech Stack

## Languages & Versions

- Python 3.8+
- Standard library modules: `json`, `urllib`, `unittest.mock`

## Dependencies

- `requests` (HTTP client for weather API calls)
- `pytest` (testing framework)
- `pytest-cov` (coverage reporting)

## Test Runner

pytest with coverage reporting

## Lint & Format Tools

- `black` (code formatting)
- `flake8` (linting)

## Dockerfile

```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "weather.py"]
```

## Conventions

### Module Layout
- `weather.py` — main script with core weather fetching and JSON serialization logic
- `test_weather.py` — unit tests with mocked weather API responses
- `requirements.txt` — dependency list

### Error Handling
- Catch `requests.RequestException` for network failures (test with mock)
- Validate JSON serialization before writing to file
- Raise `ValueError` for invalid input (e.g., empty location string)
- Log errors to stderr, continue gracefully when possible

### Testing Strategy
- Mock the weather API using `unittest.mock.patch`
- Test successful data fetch and save flow
- Test error scenarios: network failure, invalid response, file write failure
- All external dependencies mocked in unit tests

## Test Commands

| repo | command | dockerfile |
| --- | --- | --- |
| my-first-app | pytest -v --cov=. --cov-report=term-missing | Dockerfile |
