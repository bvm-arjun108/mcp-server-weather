# MCP Weather Server (Open-Meteo)

This project is a minimal MCP server built with Python and the Open-Meteo API. It exposes tools for current weather, forecasts, and geocoding-based location lookup. This README is written so you can recreate the project from scratch, step by step, without guesswork.

## What this server provides

- Tools (model-controlled):
  - `get_current_weather(latitude, longitude)`
  - `get_forecast(latitude, longitude, forecast_days=1)`
  - `get_location(name, count=5)`
- Resource (client-controlled):
  - `resource://about`

## Requirements

- Python 3.10+ (tested with 3.11)
- MCP Python SDK
- httpx

Optional but recommended:
- `uv` (fast Python package manager) if it works on your machine

## Project structure

```
mcp-server-weather/
  README.md
  requirements.txt
  pyproject.toml
  server.py
  test_tools.py
  .gitignore
```

## Step-by-step setup (manual, reliable)

Use this flow if `uv` is unavailable or unstable.

1) Create the project folder

```bash
mkdir mcp-server-weather
cd mcp-server-weather
```

2) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Create `requirements.txt`

```bash
cat <<'REQ' > requirements.txt
mcp[cli]>=1.0.0
httpx>=0.26.0
REQ
```

4) Install dependencies

```bash
pip install -r requirements.txt
```

5) Create `server.py` (MCP server)

```bash
cat <<'PY' > server.py
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1"
USER_AGENT = "weather-app/1.0"


async def make_openmeteo_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Open-Meteo API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.resource("resource://about")
async def about() -> str:
    """Describe this MCP server and its capabilities."""
    return (
        "Open-Meteo MCP server exposing tools for current weather, forecasts, "
        "and geocoding-based location lookup."
    )


@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> dict[str, Any] | str:
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = (
        f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,"
        "wind_direction_10m,pressure_msl,snowfall,precipitation,"
        "relative_humidity_2m,apparent_temperature,rain,weather_code,"
        "surface_pressure,wind_gusts_10m"
    )

    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch current weather data for this location."

    return data


@mcp.tool()
async def get_forecast(
    latitude: float, longitude: float, forecast_days: int = 1
) -> dict[str, Any] | str:
    """Get an hourly forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        forecast_days: Number of days to include (1-16)
    """
    if forecast_days < 1 or forecast_days > 16:
        return "forecast_days must be between 1 and 16."

    url = (
        f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}"
        "&hourly=temperature_2m,relative_humidity_2m,precipitation,"
        "weather_code,wind_speed_10m&timezone=auto"
        f"&forecast_days={forecast_days}"
    )

    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch forecast data for this location."

    return data


@mcp.tool()
async def get_location(name: str, count: int = 5) -> dict[str, Any] | str:
    """Find a location using the Open-Meteo Geocoding API.

    Args:
        name: City or place name to search for
        count: Maximum number of results (1-10)
    """
    if count < 1 or count > 10:
        return "count must be between 1 and 10."

    params = httpx.QueryParams(
        {
            "name": name,
            "count": count,
            "language": "en",
            "format": "json",
        }
    )
    url = f"{GEOCODING_API_BASE}/search?{params}"

    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch location data."

    return data


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
PY
```

6) Create a quick CLI test (`test_tools.py`)

```bash
cat <<'PY' > test_tools.py
import asyncio

from server import get_current_weather, get_forecast, get_location


def _print_result(label: str, result: object) -> None:
    print(f"\n=== {label} ===")
    print(result)


async def main() -> None:
    location = await get_location("Oslo", count=3)
    _print_result("get_location", location)

    if isinstance(location, dict) and location.get("results"):
        first = location["results"][0]
        latitude = first.get("latitude")
        longitude = first.get("longitude")
    else:
        latitude = 59.9139
        longitude = 10.7522

    current = await get_current_weather(latitude, longitude)
    _print_result("get_current_weather", current)

    forecast = await get_forecast(latitude, longitude, forecast_days=2)
    _print_result("get_forecast", forecast)


if __name__ == "__main__":
    asyncio.run(main())
PY
```

7) Run the quick CLI test

```bash
python test_tools.py
```

8) Run the MCP Inspector (recommended)

```bash
mcp dev server.py
```

Then open http://localhost:5173 and test tools via the UI.

## Step-by-step setup (uv, optional)

If `uv` works on your machine, you can use it for setup.

```bash
mkdir mcp-server-weather
cd mcp-server-weather
uv init
uv venv
source .venv/bin/activate
uv add "mcp[cli]" httpx
```

Then create `server.py` and `test_tools.py` using the steps above.

## Notes and tips

- Use `resource://about` for resources because MCP validates resource URIs as URLs.
- The tools return raw JSON so the client model can format and reason about the data.
- Open-Meteo endpoints used:
  - Forecast API: https://api.open-meteo.com/v1/forecast
  - Geocoding API: https://geocoding-api.open-meteo.com/v1/search

## Troubleshooting

- If `mcp` does not install, verify Python version is 3.10+.
- If `uv init` crashes on macOS, use the manual setup.
- If MCP Inspector won’t connect, confirm `mcp dev server.py` is running.
