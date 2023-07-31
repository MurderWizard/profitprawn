import pandas as pd
from datetime import datetime
from pytz import timezone
from historical_data_collection import HistoricalDataCollection
from dataprocessing import DataProcessing
from IndicatorCalculator import IndicatorCalculator
def test_module():
    # Instantiate the historical data collection object
    historical_data_collection = HistoricalDataCollection(symbol='BTC/USD:BTC')

    # Define the intervals and the start and end times
    intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    start_time = datetime(2022, 1, 1, tzinfo=timezone('UTC'))
    end_time = datetime(2022, 12, 31, tzinfo=timezone('UTC'))

    # Fetch historical data
    raw_data_dict = historical_data_collection.get_multi_timeframe_data(intervals, start_time, end_time)

    # Instantiate the data processing object and process the raw data
    data_processing = DataProcessing(raw_data_dict)
    processed_data = data_processing.get_processed_data()

    # Instantiate the indicator calculator object
    indicator_calculator = IndicatorCalculator(processed_data)

    # Define the indicators to calculate for each timeframe
    indicators_dict = {
        '1m': ['MACD', 'Bollinger Bands'],
        '5m': ['MACD', 'Bollinger Bands', 'Donchian Channel'],
        '15m': ['MACD', 'Bollinger Bands', 'Donchian Channel', 'Keltner Channel'],
        '30m': ['MACD', 'Bollinger Bands', 'Donchian Channel', 'Keltner Channel', 'RSI'],
        '1h': ['MACD', 'Bollinger Bands', 'Donchian Channel', 'Keltner Channel', 'RSI', 'VWAP'],
        '4h': ['MACD', 'Bollinger Bands', 'Donchian Channel', 'Keltner Channel', 'RSI', 'VWAP', 'VWMA'],
        '1d': ['MACD', 'Bollinger Bands', 'Donchian Channel', 'Keltner Channel', 'RSI', 'VWAP', 'VWMA', 'Fibonacci Retracement']
    }

    # Calculate the indicators
    indicators_data = indicator_calculator.calculate_technical_indicators(indicators_dict)

    # Print a summary of the results
    print("\nSummary of results:")
    for timeframe, data in indicators_data.items():
        print(f"\nTimeframe: {timeframe}")
        print(f"Number of data points: {len(data)}")
        print(f"Indicators calculated: {', '.join([column for column in data.columns if column not in ['open', 'high', 'low', 'close', 'volume']])}")
        print(f"First few rows of data:\n{data.head()}")

if __name__ == "__main__":
    test_module()
