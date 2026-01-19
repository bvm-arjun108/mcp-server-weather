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
