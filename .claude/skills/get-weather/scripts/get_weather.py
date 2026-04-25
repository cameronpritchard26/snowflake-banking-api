"""
Get current weather for a US zip code.
Usage: python get_weather.py <zip_code>
"""
import sys
import json
import re
import os
import requests

LATLNG_API_URL = "https://api.latlng.work/api"
LATLNG_API_KEY = os.environ.get("LATLNG_API_KEY", "")
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def validate_zip(zip_code: str) -> bool:
    return bool(re.fullmatch(r"\d{5}", zip_code.strip()))


def zip_to_latlng(zip_code: str) -> tuple[float, float]:
    if not LATLNG_API_KEY:
        raise RuntimeError("LATLNG_API_KEY environment variable is not set")
    resp = requests.get(
        LATLNG_API_URL,
        params={"q": zip_code},
        headers={"X-Api-Key": LATLNG_API_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    features = data.get("features", [])
    us_feature = next(
        (f for f in features if f.get("properties", {}).get("countrycode") == "US"),
        None,
    )
    if not us_feature:
        raise ValueError(f"No US location found for zip code {zip_code}")

    coords = us_feature["geometry"]["coordinates"]
    lon, lat = coords[0], coords[1]
    return lat, lon


def get_weather(lat: float, lon: float) -> dict:
    resp = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    current = data["current"]
    weather_code = current["weather_code"]

    return {
        "temperature": f"{current['temperature_2m']}°F",
        "humidity": f"{current['relative_humidity_2m']}%",
        "wind_speed": f"{current['wind_speed_10m']} mph",
        "weather_condition": WMO_CODES.get(weather_code, f"Unknown (code {weather_code})"),
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "MISSING_ZIP", "message": "No zip code provided"}))
        sys.exit(1)

    zip_code = sys.argv[1].strip()

    if not validate_zip(zip_code):
        print(json.dumps({"error": "INVALID_ZIP", "message": f"'{zip_code}' is not a valid 5-digit US zip code"}))
        sys.exit(1)

    try:
        lat, lon = zip_to_latlng(zip_code)
    except ValueError as e:
        print(json.dumps({"error": "INVALID_ZIP", "message": str(e)}))
        sys.exit(1)
    except requests.HTTPError as e:
        print(json.dumps({"error": "API_ERROR", "message": f"Location lookup failed: {e}"}))
        sys.exit(1)

    try:
        weather = get_weather(lat, lon)
    except requests.HTTPError as e:
        print(json.dumps({"error": "API_ERROR", "message": f"Weather fetch failed: {e}"}))
        sys.exit(1)

    weather["zip_code"] = zip_code
    weather["latitude"] = lat
    weather["longitude"] = lon
    print(json.dumps(weather, indent=2))


if __name__ == "__main__":
    main()
