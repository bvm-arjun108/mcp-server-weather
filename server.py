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
