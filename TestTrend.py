import unittest
import pandas as pd
from dataprocessing import DataProcessing
from trendidentification import TrendIdentification
from historical_data_collection import HistoricalDataCollection
from datetime import datetime


class TrendIdentificationTest(unittest.TestCase):
    def test_trend_identification(self):
        # Initialize the HistoricalDataCollection object
        hdc = HistoricalDataCollection('BTCUSDT')

        # Fetch the raw data
        start_time = datetime.strptime('2023-06-09', '%Y-%m-%d')
        end_time = datetime.strptime('2023-07-09', '%Y-%m-%d')
        raw_data_dict = hdc.get_multi_timeframe_data(['1h'], start_time, end_time)

        # Initialize the DataProcessing object with the raw data
        dp = DataProcessing(raw_data_dict)
        ti = TrendIdentification(dp)

        # Process data and calculate indicators
        processed_data = dp.process_data('1h', start_time)
        indicators_dict = {'1h': ['MACD', 'Bollinger Bands', 'RSI', 'VWMA']}  # Define the indicators to calculate

        for timeframe in indicators_dict.keys():
            for indicator in indicators_dict[timeframe]:
                processed_data = dp.calculate_indicator(processed_data, indicator)

            # Identify trend
            trend = ti.identify_trend_vwma_fibonacci_rsi(processed_data, processed_data)

            # TODO: Add assertions to check the output
            # For example:
            # self.assertEqual(trend, expected_trend)

            # Call calculate_VWMA on the dp object, not self.data_processor
            vwma_30m = dp.calculate_VWMA('30m')

            # TODO: Add assertions to check the output
            # For example:
            # self.assertEqual(vwma_30m, expected_vwma_30m)


if __name__ == "__main__":
    unittest.main()
