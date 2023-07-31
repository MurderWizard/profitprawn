import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from historical_data_collection import HistoricalDataCollection
from dataprocessing import DataProcessing  # Assuming the DataProcessing class is in a file named data_processing.py
from IndicatorCalculator import IndicatorCalculator

# Load the API key and secret from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

api_key = config['api_key']
api_secret = config['api_secret']

symbol = 'BTC/USD:BTC'  # Don't forget to quote the symbol correctly

# Initialize the HistoricalDataCollection object
data_collector = HistoricalDataCollection(symbol=symbol)

# Fetch data for the 1d timeframe
timeframe = '1m'
try:
    limit = 55  # Fetch 55 periods of 1d data
    start_time = pd.to_datetime(
        (datetime.now(timezone('UTC')) - timedelta(days=limit)).replace(hour=0, minute=0, second=0, microsecond=0))

    print(f"Start time: {start_time}, Type: {type(start_time)}")

    df = data_collector.get_historical_data(timeframe, start_time, num_periods=limit)

    print(f"Data fetched: {df.head()}")

    # Initialize the DataProcessing object
    data_processor = DataProcessing({timeframe: df})

    # Process the data
    processed_data = data_processor.process_data(timeframe, start_time)

    # Print the processed data points
    print(f"Processed data available for {timeframe} interval:")
    print(processed_data)
    print()

    # Check if we have at least 55 periods
    assert len(
        processed_data) >= 55, f"Insufficient data for {timeframe} timeframe. Minimum required periods: 55, available periods: {len(processed_data)}"

    # Initialize the IndicatorCalculator object
    indicator_calculator = IndicatorCalculator(processed_data)

    # Calculate and print each indicator
    for indicator in ["MACD", "Bollinger Bands", "Donchian Channel", "Keltner Channel", "RSI", "VWAP", "VWMA", "Fibonacci Retracement", "ATR"]:
        print(f"\n{indicator} for {timeframe} interval:")
        print(indicator_calculator.calculate_indicator(timeframe, indicator))

except Exception as e:
    print(f"Error fetching and processing data for {timeframe} interval: {e}\n")
