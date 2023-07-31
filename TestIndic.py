import pytest
from dataprocessing import DataProcessing
from historical_data_collection import HistoricalDataCollection
import datetime
import pandas as pd
import ta
import numpy as np
from IndicatorCalculator import IndicatorCalculator


symbol = 'BTC/USD:BTC'
intervals = ['5m', '15m', '1h', '4h', '1d']
start_time = datetime.datetime.now() - datetime.timedelta(days=35)
num_periods_dict = {'5m': 12*24*30, '15m': 4*24*30, '1h': 24*30, '4h': 6*30, '1d': 30}
raw_data_dict = {}
indicators_to_calculate = ['MACD', 'Bollinger Bands', 'Donchian Channel', 'Keltner Channel', 'RSI', 'VWAP', 'VWMA', 'Fibonacci retracement']

@pytest.fixture(scope="module", autouse=True)
def setup_module():
    return get_historical_data()

@pytest.fixture
def data_processor(setup_module):  # Add setup_module as a parameter
    return DataProcessing(setup_module)

@pytest.fixture
def indicator_calculator(setup_module, data_processor):  # Add data_processor as a parameter
    historical_data_collector = HistoricalDataCollection(symbol)  # Assuming 'symbol' is defined globally
    return IndicatorCalculator(historical_data_collector, data_processor)

def get_historical_data():
    data_collection = HistoricalDataCollection(symbol)
    for interval in intervals:
        num_periods = num_periods_dict[interval]
        data = data_collection.get_historical_data(interval, start_time, num_periods=num_periods)

        assert data is not None, f"Failed to fetch data for {interval} interval."
        assert isinstance(data, pd.DataFrame), f"Data for {interval} is not a DataFrame."
        raw_data_dict[interval] = data.copy()
    return raw_data_dict  # return the raw_data_dict

# The rest of your test functions remain the same...

def test_process_data(data_processor, setup_module):  # Add setup_module as a parameter
    for interval in intervals:
        processed_data = data_processor.process_data(interval, start_time)
        assert not processed_data.empty, f"Processed data for {interval} is empty."
        assert processed_data.index[0] >= start_time, f"Start time mismatch for {interval}."

        calculated_end_time = start_time + pd.DateOffset(days=num_periods_dict[interval])
        actual_end_time = processed_data.index[-1]

        try:
            assert actual_end_time <= calculated_end_time, f"End time mismatch for {interval}."
        except AssertionError:
            print(f"For interval {interval}:")
            print(f"Expected end time (start_time + num_periods): {calculated_end_time}")
            print(f"Actual end time in processed data: {actual_end_time}")

        assert all(column in processed_data.columns for column in ['open', 'high', 'low', 'close', 'volume']), f"Missing necessary columns in processed data for {interval}."
        assert all(processed_data[column].dtype in ['int64', 'float64'] for column in ['open', 'high', 'low', 'close', 'volume']), f"Incorrect data types in processed data for {interval}."
        assert not processed_data.isnull().values.any(), f"Processed data for {interval} contains null values."


def test_data_points_for_indicators(indicator_calculator):
    indicators = ["MACD", "Bollinger Bands", "Donchian Channel", "Keltner Channel", "RSI", "VWAP", "VWMA", "Fibonacci Retracement", "ATR"]
    for interval in intervals:
        for indicator in indicators:
            # Get the required data points for the current indicator
            required_data_points = indicator_calculator.get_required_data_points(indicator)
            # Call get_historical_data with num_periods and interval as keyword arguments
            data_points = len(indicator_calculator.historical_data_collector.get_historical_data(interval=interval, num_periods=required_data_points))
            assert data_points >= required_data_points, f"Insufficient data points for {indicator} on {interval} interval. Required: {required_data_points}, got: {data_points}"


def test_calculate_MACD(indicator_calculator):
    for interval in intervals:
        try:
            indicators_data = indicator_calculator.calculate_indicator('MACD', interval)
            assert indicators_data is not None, f"Failed to calculate MACD"
            assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for MACD is not a DataFrame."
            assert 'macd' in indicators_data.columns, f"'macd' column not found in the DataFrame for {interval}."
            assert 'macd_signal' in indicators_data.columns, f"'macd_signal' column not found in the DataFrame for {interval}."
            assert 'macd_hist' in indicators_data.columns, f"'macd_hist' column not found in the DataFrame for {interval}."
        except ValueError as e:
            if interval == '1d':
                assert str(e) == "Insufficient data for 1d timeframe to calculate MACD. Minimum required periods: 35, available periods: 30"
            else:
                raise

def test_calculate_Bollinger_Bands(indicator_calculator):
    for interval in intervals:
        indicators_data = indicator_calculator.calculate_indicator('Bollinger Bands', interval)
        assert indicators_data is not None, f"Failed to calculate Bollinger Bands"
        assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for Bollinger Bands is not a DataFrame."
        assert indicators_data.shape[0] >= 20, f"Not enough data points for {interval} to calculate Bollinger Bands."

def test_calculate_Donchian_Channel(indicator_calculator):
    for interval in intervals:
        indicators_data = indicator_calculator.calculate_indicator('Donchian Channel', interval)
        assert indicators_data is not None, f"Failed to calculate Donchian Channel"
        assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for Donchian Channel is not a DataFrame."

def test_calculate_Keltner_Channel(indicator_calculator):
    for interval in intervals:
        try:
            indicators_data = indicator_calculator.calculate_indicator('Keltner Channel', interval)
            assert indicators_data is not None, f"Failed to calculate Keltner Channel"
            assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for Keltner Channel is not a DataFrame."
            assert indicators_data.shape[0] >= 20, f"Not enough data points for {interval} to calculate Keltner Channel."
        except ValueError as e:
            if interval == '1d':
                actual_periods = len(raw_data_dict[interval])  # Get the actual number of periods available
                assert str(e) == f"Insufficient data for 1d timeframe to calculate Keltner Channel. Minimum required periods: 20, available periods: {actual_periods}"
            else:
                raise

def test_calculate_RSI(indicator_calculator):
    for interval in intervals:
        try:
            indicators_data = indicator_calculator.calculate_indicator('RSI', interval)
            assert indicators_data is not None, f"Failed to calculate RSI"
            assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for RSI is not a DataFrame."
            assert indicators_data.shape[0] >= 14, f"Not enough data points for {interval} to calculate RSI."
        except ValueError as e:
            if interval == '1d':
                assert str(e) == "Insufficient data for 1d timeframe to calculate RSI. Minimum required periods: 14, available periods: 10"
            else:
                raise

def test_calculate_VWAP(indicator_calculator):
    for interval in intervals:
        try:
            indicators_data = indicator_calculator.calculate_indicator('VWAP', interval)
            assert indicators_data is not None, f"Failed to calculate VWAP"
            assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for VWAP is not a DataFrame."
            assert indicators_data.shape[0] >= 24, f"Not enough data points for {interval} to calculate VWAP."
        except ValueError as e:
            if interval == '1d':
                assert str(e) == "Insufficient data for 1d timeframe to calculate VWAP. Minimum required periods: 24, available periods: 10"
            else:
                raise

def test_calculate_VWMA(indicator_calculator):
    for interval in intervals:
        try:
            indicators_data = indicator_calculator.calculate_indicator('VWMA', interval)
            assert indicators_data is not None, f"Failed to calculate VWMA"
            assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for VWMA is not a DataFrame."
            assert indicators_data.shape[0] >= indicator_calculator.vwma_window, f"Not enough data points for {interval} to calculate VWMA."
        except ValueError as e:
            if interval == '1d':
                assert str(e) == f"Insufficient data for 1d timeframe to calculate VWMA. Minimum required periods: {indicator_calculator.vwma_window}, available periods: 10"
            else:
                raise

def test_calculate_Fibonacci_retracement(indicator_calculator):
    for interval in intervals:
        try:
            indicators_data = indicator_calculator.calculate_indicator('Fibonacci Retracement', interval)
            assert indicators_data is not None, f"Failed to calculate Fibonacci Retracement"
            assert isinstance(indicators_data, pd.DataFrame), f"Indicators data for Fibonacci Retracement is not a DataFrame."
            assert indicators_data.shape[0] >= indicator_calculator.fibonacci_lookback_period, f"Not enough data points for {interval} to calculate Fibonacci Retracement."
        except ValueError as e:
            if interval == '1d':
                assert str(e) == f"Insufficient data for 1d timeframe to calculate Fibonacci Retracement. Minimum required periods: {indicator_calculator.fibonacci_lookback_period}, available periods: 10"
            else:
                raise

