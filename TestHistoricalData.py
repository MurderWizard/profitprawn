import unittest
import pandas as pd
import numpy as np
import datetime
from historical_data_collection import HistoricalDataCollection

class TestHistoricalDataCollection(unittest.TestCase):
    def setUp(self):
        self.symbol = 'BTC/USD:BTC'
        self.data_collection = HistoricalDataCollection(symbol=self.symbol)
        self.test_summary = {}

    def tearDown(self):
        self.print_test_summary()  # Print the test summary after each test
        self.test_summary = {}  # Reset the test summary after each test

    def test_data_availability(self):
        intervals = ['1m', '15m', '1h', '1d', '1w', '1M', '1y']
        num_periods_dict = {
            '1m': 60,  # Get 1 hour of '1m' data
            '15m': 60,  # Get 15 hours of '15m' data
            '1h': 12,  # Get 12 hours of '1h' data
            '1d': 7,  # Get 1 week of '1d' data
            '1w': 4,  # Get 1 month of '1w' data
            '1M': 4,  # Get 4 months of '1M' data
            '1y': 1 # Get 1 year of '1Y' data
        }
        end_time = datetime.datetime.now() - datetime.timedelta(days=7)  # Set end_time to 7 days ago
        start_times = {
            '1m': end_time - datetime.timedelta(hours=1),
            '15m': end_time - datetime.timedelta(hours=15),
            '1h': end_time - datetime.timedelta(hours=12),
            '1d': end_time - datetime.timedelta(days=7),
            '1w': end_time - datetime.timedelta(weeks=4),
            '1M': end_time - datetime.timedelta(weeks=4*4),  # Assuming a month is 4 weeks
            '1y': end_time - datetime.timedelta(days=365)  # Assuming a year is 365 days
        }
        for interval in intervals:
            num_periods = num_periods_dict[interval]
            data = self.data_collection.get_historical_data(interval, start_times[interval], num_periods)
            if data.empty:
                self.test_summary[f"Data availability for '{interval}' data"] = "Data is not available."
            else:
                self.test_summary[f"Data availability for '{interval}' data"] = f"Data is available with {data.shape[0]} rows."

    def print_test_summary(self):
        print("\nTest Summary:")
        for test, result in self.test_summary.items():
            print(f"{test}: {result}")

if __name__ == '__main__':
    unittest.main()
