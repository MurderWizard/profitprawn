from datetime import datetime, timedelta
from historical_data_collection import HistoricalDataCollection
from dataprocessing import DataProcessing
from IndicatorCalculator import IndicatorCalculator

class DebugModule:
    def __init__(self, data_collection, data_processing, indicator_calculator):
        self.data_collection = data_collection
        self.data_processing = data_processing
        self.indicator_calculator = indicator_calculator

    def debug(self):
        intervals = ['5m', '15m', '1h', '4h', '1d']  # Define your intervals
        start_time = datetime.now() - timedelta(weeks=1)
        end_time = datetime.now()

        try:
            raw_data_dict = self.data_collection.get_multi_timeframe_data(intervals, start_time, end_time)
        except Exception as e:
            print("Error occurred during data collection: ", str(e))
            return

        processed_data_dict = {}
        for interval in intervals:
            try:
                processed_data = self.data_processing.process_data(interval, start_time)
                if processed_data.empty:
                    print(f"No data available for {interval} interval.")
                    continue
                processed_data_dict[interval] = processed_data
            except Exception as e:
                print(f"Error occurred during data processing for {interval} interval: ", str(e))
                return

        try:
            # You need to specify the timeframe and the indicator you want to calculate
            for timeframe in processed_data_dict.keys():
                for indicator in ['MACD', 'Bollinger Bands', 'Donchian Channel', 'Keltner Channel', 'RSI', 'VWAP', 'VWMA', 'Fibonacci Retracement', 'ATR']:  # replace with your indicators
                    self.indicator_calculator.calculate_indicator(timeframe, indicator)
        except Exception as e:
            print("Error occurred during indicator calculation: ", str(e))
            return

        print("No errors detected.")

# Initialize the classes
data_collection = HistoricalDataCollection(symbol='BTC/USD:BTC')

# Define the start_time and end_time
start_time = datetime.now() - timedelta(weeks=1)
end_time = datetime.now()

# Get the raw data
raw_data_dict = data_collection.get_multi_timeframe_data(['5m', '15m', '1h', '4h', '1d'], start_time, end_time)

# Initialize the DataProcessing class with the raw_data_dict
data_processing = DataProcessing(raw_data_dict)

# Process the data for each interval and store it in a dictionary
processed_data_dict = {}
for interval in ['5m', '15m', '1h', '4h', '1d']:
    processed_data = data_processing.process_data(interval, start_time)
    if not processed_data.empty:
        processed_data_dict[interval] = processed_data

# Create an IndicatorCalculator object
indicator_calculator = IndicatorCalculator(processed_data_dict)

# Create a DebugModule object
debug_module = DebugModule(data_collection, data_processing, indicator_calculator)

# Call the debug method
debug_module.debug()
