import ccxt
import pandas as pd
import pytz
from datetime import datetime, timedelta

# Instantiate the ccxt.phemex instance
phemex = ccxt.phemex({
    'apiKey': 'your_api_key',
    'secret': 'your_api_secret'
})

def test_fetch_ohlcv_with_start_time():
    utc = pytz.timezone('UTC')  # Define timezone
    symbol = 'ETHUSD'  # Add your symbol
    timeframe = '4h'  # Add your timeframe
    limit = 100  # Number of data points to fetch
    start_time = datetime(2022, 1, 1, 0, 0, tzinfo=utc)  # start_time is now timezone aware

    bars = phemex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, since=int(start_time.timestamp() * 1000))
    df_sma = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_sma['timestamp'] = pd.to_datetime(df_sma['timestamp'], unit='ms')

    actual_start_time = df_sma['timestamp'].iloc[0].tz_localize(utc)  # Make actual_start_time tz-aware
    time_difference = actual_start_time - start_time

    print(f"Requested start time: {start_time}")
    print(f"Actual start time: {actual_start_time}")
    print(f"Time difference: {time_difference}")

    assert actual_start_time >= start_time, "Start time in the data is before the provided start time."

test_fetch_ohlcv_with_start_time()

