import ccxt
import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from pytz import timezone
from IndicatorCalculator import IndicatorCalculator

class HistoricalDataCollection:
    def __init__(self, symbol='BTC/USD:BTC', indicator_calculator=None, event=None):
        with open('config.json') as config_file:
            config = json.load(config_file)

        self.exchange = ccxt.phemex({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'enableRateLimit': True
        })
        self.symbol = symbol
        self.timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '3h', '4h', '6h', '12h', '1d', '1w', '1M', '3M', ]  # Define timeframes here
        self.indicator_calculator = indicator_calculator if indicator_calculator else IndicatorCalculator()
        self.event = event

    def get_interval_in_seconds(self, interval):
        multiplier = int(interval[:-1])
        if 'm' in interval:
            return multiplier * 60  # minutes to seconds
        elif 'h' in interval:
            return multiplier * 60 * 60  # hours to seconds
        elif 'd' in interval:
            return multiplier * 24 * 60 * 60  # days to seconds
        elif 'M' in interval:
            return multiplier * 30 * 24 * 60 * 60  # months to seconds
        elif 'w' in interval:
            return multiplier * 7 * 24 * 60 * 60  # weeks to seconds
        elif 'y' in interval:
            return multiplier * 365 * 24 * 60 * 60  # years to seconds
        else:
            raise ValueError(f"Invalid interval: {interval}")

    def calculate_time_delta(self, interval):
        if 'm' in interval:
            minutes = int(interval[:-1])
            return timedelta(minutes=minutes)
        elif 'h' in interval:
            hours = int(interval[:-1])
            return timedelta(hours=hours)
        elif 'd' in interval:
            days = int(interval[:-1])
            return timedelta(days=days)
        elif 'w' in interval:
            weeks = int(interval[:-1])
            return timedelta(weeks=weeks)
        elif 'M' in interval:
            months = int(interval[:-1])
            return relativedelta(months=months)
        else:
            raise ValueError(f"Invalid interval: {interval}")

    def calculate_start_time(self, interval, num_periods=1):
        utc = timezone('UTC')
        current_time = datetime.now(utc)
        interval_seconds = self.get_interval_in_seconds(interval)
        start_time = current_time - timedelta(seconds=num_periods * interval_seconds)
        return start_time

    def fetch_data_from_api(self, symbol, interval, current_time):
        since_param = int(current_time.timestamp()) * 1000  # Convert to milliseconds
        print(f"since_param: {since_param}")
        return self.exchange.fetch_ohlcv(symbol, interval, since=since_param)

    def process_api_response(self, ohlcv_data, current_time, interval_seconds, utc, empty_responses):
        total_data = []
        if ohlcv_data and not any(isinstance(x, type(None)) for x in ohlcv_data[0]):
            total_data += ohlcv_data
            print(f"Total data after appending: {total_data}")
            last_timestamp = ohlcv_data[-1][0]
            print(f"Last timestamp: {last_timestamp}")
            current_time = datetime.fromtimestamp(last_timestamp / 1000, utc) + timedelta(
                seconds=interval_seconds)
            print(f"Updated current_time: {current_time}")
            consecutive_errors = 0
            empty_responses = 0
        else:
            current_time = current_time + timedelta(seconds=interval_seconds)
            print(f"No data fetched. Updated current_time: {current_time}")
            empty_responses += 1
        return total_data, current_time, consecutive_errors, empty_responses

    def get_historical_data(self, interval, indicator, start_time=None, num_periods=1, symbol=None):
        utc = timezone('UTC')

        if start_time is None:
            start_time = self.calculate_start_time(interval, num_periods)
        elif start_time.tzinfo is None:
            start_time = utc.localize(start_time)

        if symbol is None:
            symbol = self.symbol

        print(f"Fetching data for {interval} interval for symbol {symbol}...")

        interval_seconds = self.get_interval_in_seconds(interval)
        print(f"Interval in seconds: {interval_seconds}")

        # Get the required number of data points for the given indicator
        required_data_points = self.indicator_calculator.get_required_data_points(indicator)

        total_data = []

        current_time = start_time
        max_consecutive_errors = 3
        consecutive_errors = 0

        max_empty_responses = 10
        empty_responses = 0

        max_attempts = 10  # Maximum number of attempts to fetch data
        attempts = 0  # Counter for the number of attempts

        while (num_periods is None or len(total_data) < num_periods) and attempts < max_attempts:
            print(f"Current time: {current_time}")
            print(f"Number of periods: {num_periods}")
            print(f"Total data length: {len(total_data)}")
            print(f"Number of attempts: {attempts}")

            attempts += 1  # Increment the attempts counter

            try:
                if current_time > datetime.now(utc):  # Updated line
                    print(
                        f"Cannot fetch data for future date {current_time}. Stopping data fetch for {interval} interval.")
                    break

                ohlcv_data = self.fetch_data_from_api(symbol, interval, current_time)
                print(f"API response: {ohlcv_data}")

                if not ohlcv_data:  # If the data is empty
                    print(f"No data returned for {interval} interval.")
                    break  # Break the loop

                total_data, current_time, consecutive_errors, empty_responses = self.process_api_response(ohlcv_data,
                                                                                                          current_time,
                                                                                                          interval_seconds,
                                                                                                          utc,
                                                                                                          empty_responses)

            except ccxt.ExchangeError as e:
                print(f"Error fetching data for {interval} interval: {e}")
                break  # Break the loop if an error occurs

            time.sleep(self.exchange.rateLimit / 1000)

        df = pd.DataFrame(total_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        if 'time' in df.columns and not df['time'].isnull().any():
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index('time', inplace=True, drop=True)
        else:
            print("Error: 'time' column not found or contains NaN values.")
            return pd.DataFrame()

        # Convert the index to Timestamp objects
        df.index = pd.to_datetime(df.index)

        df = df.loc[~df.index.duplicated(keep='first')]
        df = df.sort_index()

        # Update the number of periods based on the actual data
        num_periods = len(df)

        # Emit an event with the fetched data
        if self.event:
            self.event.emit(df)

        return df
