import unittest
import ccxt
import datetime
from historical_data_collection import HistoricalDataCollection

class HistoricalDataFetchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set the symbol and intervals
        cls.symbol = 'BTC/USDT'
        cls.intervals = ['1m', '5m', '15m', '1h', '4h']

        # Create a HistoricalDataCollection instance
        cls.historical_data = HistoricalDataCollection(cls.symbol)

        # Define the start and end times for the data
        cls.end_time = datetime.datetime.now()
        cls.start_time = cls.end_time - datetime.timedelta(days=1)  # Get the last 1 day of data

    def _test_api_response(self, interval):
        try:
            # Fetch the historical data for the interval
            data = self.historical_data.get_historical_data(interval, self.start_time, self.end_time)

            # Check if the API returned data
            self.assertIsNotNone(data, f"No data returned from API for {interval} interval.")
            self.assertGreater(len(data), 0, f"Empty data returned from API for {interval} interval.")

            print(f"API returned {len(data)} rows of data for {interval} interval.")

        except ccxt.ExchangeError as e:
            self.fail(f"ExchangeError occurred while fetching {interval} data: {str(e)}")
        except Exception as e:
            self.fail(f"Unexpected error occurred while fetching {interval} data: {str(e)}")

    def test_1m_data(self):
        self._test_api_response('1m')

    def test_5m_data(self):
        self._test_api_response('5m')

    def test_15m_data(self):
        self._test_api_response('15m')

    def test_1h_data(self):
        self._test_api_response('1h')

    def test_4h_data(self):
        self._test_api_response('4h')


if __name__ == '__main__':
    unittest.main(verbosity=2)
