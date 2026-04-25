---
name: get-weather
description: Get current weather conditions for a US zip code. Returns temperature, humidity, wind speed, and weather condition as JSON. Uses latlng.work for geocoding and open-meteo.com for weather data.
---

# get-weather

Fetches current weather for a US zip code using the latlng.work geocoding API and open-meteo.com weather API.

## How to invoke

When the user runs `/get-weather <zip_code>`:

1. **If no zip code was provided** — ask the user: "Please provide a US zip code to get the weather for."
2. **If the zip code looks invalid** (not 5 digits) — ask the user: "That doesn't look like a valid US zip code. Please provide a 5-digit zip code (e.g., 90210)."
3. **If a zip code is present**, run the Python script:

```bash
cd .claude/skills/get-weather && python scripts/get_weather.py <zip_code>
```

Or on Windows if `python` is not found:

```powershell
cd .claude\skills\get-weather; & "C:\Users\ralph\AppData\Local\Microsoft\WindowsApps\python.exe" scripts/get_weather.py <zip_code>
```

## Handling script output

The script returns JSON. Parse and display it in a friendly format, for example:

```
Weather for 90210 (Beverly Hills, CA):
  Temperature:  72.3°F
  Humidity:     58%
  Wind Speed:   8.2 mph
  Condition:    Partly cloudy
```

### Error responses

If the JSON contains an `"error"` key, handle it:

| error code    | Action                                                                 |
|---------------|------------------------------------------------------------------------|
| `MISSING_ZIP` | Ask the user for a zip code                                            |
| `INVALID_ZIP` | Tell the user the zip code is invalid and ask for a valid 5-digit one  |
| `API_ERROR`   | Display the `message` field and suggest trying again                   |

## Example successful response

```json
{
  "temperature": "72.3°F",
  "humidity": "58%",
  "wind_speed": "8.2 mph",
  "weather_condition": "Partly cloudy",
  "zip_code": "90210",
  "latitude": 34.0901,
  "longitude": -118.4065
}
```

## Dependencies

Install with:
```bash
pip install requests
```

- **latlng.work** — converts zip code to lat/lng (`X-Api-Key` header auth)
- **open-meteo.com** — provides current weather data (no API key required)
