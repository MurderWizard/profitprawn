import unittest
from datetime import datetime, timedelta
from pytz import timezone
from historical_data_collection import HistoricalDataCollection
from dataprocessing import DataProcessing
from IndicatorCalculator import IndicatorCalculator
from supportresistance import SupportResistance
from signalgeneration import SignalGeneration

class TestSignalGeneration(unittest.TestCase):
    def setUp(self):
        # Initialize classes for data collection, processing, indicator calculation, and support/resistance calculation
        self.historical_data_collection = HistoricalDataCollection(symbol='BTC/USD:BTC')
        raw_data_dict = self.historical_data_collection.get_multi_timeframe_data(['1h', '4h', '1w'], start_time=datetime.now() - timedelta(weeks=1), end_time=datetime.now())
        self.data_processing = DataProcessing(raw_data_dict)
        self.indicator_calculator = IndicatorCalculator(self.data_processing.get_processed_data())
        self.support_resistance = SupportResistance(self.indicator_calculator.calculate_technical_indicators())

        # Fetch historical data
        self.raw_data = self.historical_data_collection.get_historical_data(interval='1h', start_time=datetime.now(timezone('UTC')) - timedelta(days=7))

        # Process the raw data
        self.processed_data = self.data_processing.process_data(self.raw_data)

        # Calculate technical indicators
        self.indicators_data = self.indicator_calculator.calculate_technical_indicators(self.processed_data)

        # Identify support and resistance levels
        self.support_resistance_data = self.support_resistance.identify_support_resistance(self.processed_data)

        # Create a dummy funding rate
        self.funding_rate = 0.0001  # or any other number you find suitable for your tests

        # Generate trading signals
        self.signal_generation = SignalGeneration(self.processed_data, self.indicators_data, self.funding_rate, self.support_resistance_data)
        self.signals = self.signal_generation.generate_signals()

    def test_generate_signals(self):
        # Ensure that the signal is either 'buy', 'sell', or 'neutral'
        self.assertTrue((self.signals['signal'].isin(['buy', 'sell', 'neutral'])).all())

        # Check the signal values when the trend is 'uptrend'
        uptrend_signals = self.signals.loc[self.signals['trend'] == 'uptrend', 'signal']
        self.assertTrue((uptrend_signals.isin(['buy', 'neutral'])).all())

        # Check the signal values when the trend is 'downtrend'
        downtrend_signals = self.signals.loc[self.signals['trend'] == 'downtrend', 'signal']
        self.assertTrue((downtrend_signals.isin(['sell', 'neutral'])).all())


if __name__ == '__main__':
    unittest.main()
