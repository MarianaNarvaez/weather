import json
import urllib.request
from typing import Any, Dict, Tuple

import pandas as pd
import matplotlib.pyplot as plt


def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Retrieves weather forecast data from the Open-Meteo API for a given location.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        dict: Parsed JSON response from the API.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m&timezone=auto"
    )
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def flatten_hourly_data(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Flattens the 'hourly' portion of the weather data into a DataFrame and appends metadata and units.

    Args:
        data (dict): Raw weather data from the API.

    Returns:
        pd.DataFrame: Processed and structured weather data.
    """
    hourly_df = pd.DataFrame(data['hourly'])

    # Attach top-level metadata (excluding nested keys)
    metadata = {k: v for k, v in data.items() if k not in ['hourly', 'hourly_units']}
    for key, value in metadata.items():
        hourly_df[key] = value

    # Attach units as columns with suffix "_unit"
    for key, unit in data['hourly_units'].items():
        hourly_df[f"{key}_unit"] = unit

    return hourly_df


def transform_data(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Transforms raw weather data into a clean and structured DataFrame.

    Args:
        data (dict): Raw weather data.

    Returns:
        pd.DataFrame: Cleaned DataFrame ready for analysis or visualization.
    """
    df = flatten_hourly_data(data)

    # Parse datetime and extract components
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.time
    df['time'] = df['time'].dt.date

    # Rename key columns
    df.rename(columns={
        'temperature_2m': 'temperature',
        'temperature_2m_unit': 'temperature_unit'
    }, inplace=True)

    # Reorder columns
    ordered_columns = [
        'time', 'hour', 'temperature', 'latitude', 'longitude', 'generationtime_ms',
        'utc_offset_seconds', 'timezone', 'timezone_abbreviation', 'elevation',
        'time_unit', 'temperature_unit'
    ]
    return df[ordered_columns]


def plot_temperature(df: pd.DataFrame, hours: int = 24) -> None:
    """
    Plots temperature data over time.

    Args:
        df (pd.DataFrame): Weather DataFrame.
        hours (int): Number of hourly records to include in the plot. Default is 24.
    """
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['time'].astype(str) + ' ' + df['hour'].astype(str))

    plt.figure(figsize=(12, 5))
    plt.plot(df['datetime'][:hours], df['temperature'][:hours], marker='o', linestyle='-', label='Temperature')

    plt.xlabel("Datetime")
    plt.ylabel(f"Temperature ({df['temperature_unit'].iloc[0]})")
    plt.title("Temperature by Hour")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.show()


def main(lat: float, lon: float) -> None:

    raw_data = get_weather(lat, lon)
    weather_df = transform_data(raw_data)

    print(weather_df.head())
    plot_temperature(weather_df)


if __name__ == "__main__":
    main(lat=4.0, lon=-10.0)