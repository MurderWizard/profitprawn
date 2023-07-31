import unittest
import pandas as pd
import numpy as np
import datetime
from historical_data_collection import HistoricalDataCollection
from dataprocessing import DataProcessing
from pytz import timezone

def interval_to_pandas_freq(interval):
    if interval.endswith('m'):
        return '1T' if interval[:-1] == '1' else interval[:-1] + 'T'  # Convert 'm' to 'T' for minutes
    elif interval.endswith('h'):
        return interval[:-1] + 'H'  # Return 'H' for hours
    elif interval.endswith('d'):
        return 'D'  # Return 'D' for days
    else:
        raise ValueError(f"Unknown interval: {interval}")

class TestDataProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_summary = {}  # Initialize the test summary

    def setUp(self):
        end_time = datetime.datetime.now() - datetime.timedelta(days=30)  # Set end_time to 7 days ago
        data_collection = HistoricalDataCollection(symbol='BTC/USD:BTC')
        intervals = ['1m', '1h', '1d', '1w', '1M']  # Intervals to test
        num_periods_dict = {
            '1m': 60,  # Get 1 hour of '1m' data
            '1h': 12,  # Get 12 hours of '1h' data
            '1d': 7,  # Get 1 week of '1d' data
            '1w': 4,  # Get 1 month of '1w' data
            '1M': 4  # Get 4 months of '1M' data
        }
        start_times = {
            '1m': end_time - datetime.timedelta(hours=1),
            '1h': end_time - datetime.timedelta(hours=12),
            '1d': end_time - datetime.timedelta(days=7),
            '1w': end_time - datetime.timedelta(weeks=4),
            '1M': min(end_time - datetime.timedelta(weeks=4 * 4), end_time - datetime.timedelta(days=1))
            # Assuming a month is 4 weeks, but not exceeding end_time
        }
        raw_data_dict = {}
        for interval in intervals:
            num_periods = num_periods_dict[interval]
            raw_data_dict[interval] = data_collection.get_historical_data(interval, start_times[interval], num_periods)
        self.dp = DataProcessing(raw_data_dict)

    def tearDown(self):
        pass  # Do nothing in tearDown

    @classmethod
    def tearDownClass(cls):
        cls.print_test_summary()  # Print the test summary after all tests

    def test_irregular_frequency_in_data(self):
        intervals = ['1m', '1h', '1d', '1w', '1M']
        for interval in intervals:
            df = self.dp.processed_data[interval]
            if df.empty:
                continue
            time_diff = df.index.to_series().diff()
            expected_time_diff = pd.Timedelta(minutes=1) if interval == '1m' else \
                pd.Timedelta(hours=1) if interval == '1h' else \
                    pd.Timedelta(days=1) if interval == '1d' else \
                        pd.Timedelta(weeks=1) if interval == '1w' else \
                            pd.Timedelta(days=30)  # Assuming a month is 30 days
            irregular_timestamps = df.index[time_diff != expected_time_diff]
            self.assertFalse(irregular_timestamps, f"Found {len(irregular_timestamps)} irregular timestamps in {interval} data.")

    def test_timestamp_order(self):
        intervals = ['1m', '1h', '1d', '1w', '1M']
        for interval in intervals:
            df = self.dp.processed_data[interval]
            if df.empty:
                continue
            self.assertTrue(df.index.is_monotonic_increasing, f"Timestamps for {interval} data are not in increasing order.")

    def test_data_availability_and_columns(self):
        intervals = ['1m', '1h', '1d', '1w', '1M']
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for interval in intervals:
            df = self.dp.processed_data[interval]
            if df.empty:
                continue
            self.assertTrue(set(df.columns) >= set(required_columns), f"Missing columns in {interval} data.")
            incorrect_data_type_columns = [column for column in required_columns if df[column].dtype not in ['int64', 'float64']]
            self.assertFalse(incorrect_data_type_columns, f"Columns with incorrect data types in {interval} data: {', '.join(incorrect_data_type_columns)}.")

    def test_get_processed_data(self):
        processed_data = self.dp.get_processed_data()
        self.assertEqual(set(processed_data.keys()), set(['1m', '1h', '1d', '1w', '1M']), "Mismatch in retrieved data intervals.")

    @classmethod
    def print_test_summary(cls):
        print("\nTest Summary:")
        for test, result in cls.test_summary.items():
            print(f"{test}: {result}")

if __name__ == '__main__':
    unittest.main()
