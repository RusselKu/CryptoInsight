import requests

def fetch_api_data(url: str, params: dict = None, headers: dict = None):
    """Perform an HTTP GET request with error handling and default headers."""
    default_headers = {"User-Agent": "Airflow-ETL/1.0"}
    headers = {**default_headers, **(headers or {})}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            raise ValueError("Response content is not valid JSON")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching API data from {url}: {e}")
