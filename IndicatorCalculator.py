import pandas as pd
from pandas.api.types import is_numeric_dtype
import ta
from ta import trend
from ta import volatility
from ta import momentum
import numpy as np
import datetime
from dataprocessing import DataProcessing
from historical_data_collection import HistoricalDataCollection

class IndicatorCalculator:
    def __init__(self, historical_data_collector, data_processor, **kwargs):
        self.historical_data_collector = historical_data_collector
        self.data_processor = data_processor
        self.raw_data = {tf: self.historical_data_collector.get_historical_data(tf) for tf in self.historical_data_collector.timeframes}
        self.processed_data = {tf: self.data_processor.process_data(self.raw_data[tf], self.raw_data[tf].index[0]) for
                               tf in self.historical_data_collector.timeframes if not self.raw_data[tf].empty}

        self.timeframes = sorted(self.processed_data.keys())
        self.vwma_window = kwargs.get('vwma_window', 20)  # Set default VWMA window to 14
        self.fibonacci_lookback_period = kwargs.get('fibonacci_lookback_period', 55)  # Set default Fibonacci lookback period to 55
        self.indicators_data = {tf: None for tf in self.timeframes}
        self.params = kwargs
        self.indicator_min_periods = {
            'MACD': 35,
            'Bollinger Bands': 20,
            'Donchian Channel': 20,
            'Keltner Channel': 20,
            'RSI': 14,
            'VWAP': 24,
            'VWMA': self.vwma_window,
            'Fibonacci Retracement': self.fibonacci_lookback_period
        }



        # Validate processed_data
        for timeframe in self.timeframes:
            if not isinstance(self.processed_data[timeframe], pd.DataFrame):
                raise ValueError(f"Processed data for {timeframe} is not a valid DataFrame.")
            if self.processed_data[timeframe].empty:
                raise ValueError(f"Processed data for {timeframe} is empty.")
            self.validate_data(self.processed_data[timeframe])
            print(f"{timeframe} has {len(self.processed_data[timeframe])} periods")  # Print the number of periods for each timeframe



    def validate_data(self, df):
        nulls = df.isnull().sum()
        null_cols = nulls[nulls > 0]
        if not null_cols.empty:
            df.dropna(inplace=True)

        non_numeric_cols = [col for col in df.columns if not is_numeric_dtype(df[col])]
        if non_numeric_cols:
            raise ValueError(f"The following columns are not numeric: {non_numeric_cols}")

    def validate_indicator_requirements(self, timeframe, indicator):
        min_periods = self.indicator_min_periods.get(indicator)
        if min_periods is not None and self.processed_data[timeframe].shape[0] < min_periods:
            raise ValueError(f"Insufficient data for {timeframe} timeframe to calculate {indicator}. "
                             f"Minimum required periods: {min_periods}, available periods: {self.processed_data[timeframe].shape[0]}")

    def get_required_data_points(self, indicator):
        return self.indicator_min_periods.get(indicator, 0)

    def calculate_indicator(self, timeframe, indicator):
        required_data_points = self.get_required_data_points(indicator)
        if len(self.processed_data[timeframe]) < required_data_points:
            print(f"Error: Not enough data points to calculate {indicator} for {timeframe}. "
                  f"Required: {required_data_points}, available: {len(self.processed_data[timeframe])}")
            return

        indicators_data = self.processed_data[timeframe]
        if indicator == "MACD":
            return self.calculate_MACD(timeframe, indicators_data)
        elif indicator == "Bollinger Bands":
            return self.calculate_Bollinger_Bands(timeframe, indicators_data)
        elif indicator == "Donchian Channel":
            return self.calculate_Donchian_Channel(timeframe, indicators_data)
        elif indicator == "Keltner Channel":
            return self.calculate_Keltner_Channel(timeframe, indicators_data)
        elif indicator == "RSI":
            return self.calculate_RSI(timeframe, indicators_data)
        elif indicator == "VWAP":
            return self.calculate_VWAP(timeframe, indicators_data)
        elif indicator == "VWMA":
            return self.calculate_VWMA(timeframe, indicators_data)
        elif indicator == "Fibonacci Retracement":
            return self.calculate_fibonacci_retracement(timeframe, indicators_data)
        elif indicator == "ATR":
            return self.calculate_ATR(timeframe, indicators_data)

    def calculate_MACD(self, timeframe, indicators_data):
        if 'close' not in indicators_data.columns:
            raise ValueError(f"'close' column not found in the DataFrame for {timeframe}.")

        close_prices = indicators_data["close"]
        macd = trend.MACD(close_prices)

        indicators_data["macd"] = macd.macd()
        indicators_data["macd_signal"] = macd.macd_signal()
        indicators_data["macd_hist"] = macd.macd_diff()

        indicators_data.dropna(inplace=True)
        return indicators_data

    def calculate_Bollinger_Bands(self, timeframe, indicators_data):
        if 'close' not in indicators_data.columns:
            raise ValueError(f"'close' column not found in the DataFrame for {timeframe}.")

        close_prices = indicators_data["close"]
        bollinger_bands = ta.volatility.BollingerBands(close_prices)

        indicators_data["bb_bbm"] = bollinger_bands.bollinger_mavg().fillna(method='bfill')
        indicators_data["bb_bbh"] = bollinger_bands.bollinger_hband().fillna(method='bfill')
        indicators_data["bb_bbl"] = bollinger_bands.bollinger_lband().fillna(method='bfill')
        return indicators_data

    def calculate_Donchian_Channel(self, timeframe, indicators_data):
        high_prices = indicators_data["high"]
        low_prices = indicators_data["low"]
        close_prices = indicators_data["close"]

        donchian_channel = ta.volatility.DonchianChannel(high_prices, low_prices, close_prices)

        indicators_data["dc_high"] = donchian_channel.donchian_channel_hband()
        indicators_data["dc_low"] = donchian_channel.donchian_channel_lband()
        return indicators_data

    def calculate_Keltner_Channel(self, timeframe, indicators_data):
        keltner_channel = ta.volatility.KeltnerChannel(
            indicators_data["high"], indicators_data["low"], indicators_data["close"]
        )
        indicators_data["kc_high"] = keltner_channel.keltner_channel_hband()
        indicators_data["kc_low"] = keltner_channel.keltner_channel_lband()
        return indicators_data

    def calculate_RSI(self, timeframe, indicators_data):
        if self.processed_data[timeframe] is None or self.processed_data[timeframe].empty:
            raise ValueError(f"Processed data for {timeframe} is empty.")

        rsi_period = self.params.get('rsi_period', 14)  # Get RSI period from self.params
        indicators_data['rsi'] = ta.momentum.RSIIndicator(
            self.processed_data[timeframe]['close'],
            window=rsi_period
        ).rsi()
        return indicators_data

    def calculate_VWAP(self, timeframe, indicators_data):
        if 'volume' not in indicators_data.columns or 'high' not in indicators_data.columns or \
                'low' not in indicators_data.columns or 'close' not in indicators_data.columns:
            raise ValueError(f"'volume', 'high', 'low', or 'close' columns not found in the DataFrame for {timeframe}.")

        df = indicators_data.copy()

        df['volXclose'] = df['volume'] * ((df['high'] + df['low'] + df['close']) / 3)
        df['cum_vol'] = df['volume'].cumsum()
        df['cum_volXclose'] = df['volXclose'].cumsum()
        df['VWAP'] = df['cum_volXclose'] / df['cum_vol']
        df.fillna(0, inplace=True)

        indicators_data = df
        return indicators_data

    def calculate_VWMA(self, timeframe, indicators_data):
        if 'volume' not in indicators_data.columns or 'close' not in indicators_data.columns:
            raise ValueError(f"'volume' or 'close' columns not found in the DataFrame for {timeframe}.")

        df = indicators_data.copy()

        vwma = ta.volume.VolumeWeightedAveragePrice(df['high'], df['low'], df['close'], df['volume'], window=self.vwma_window).volume_weighted_average_price()
        df[f'vwma_{self.vwma_window}'] = vwma

        indicators_data = df
        return indicators_data

    def calculate_fibonacci_retracement(self, timeframe, indicators_data):
        if 'close' not in indicators_data.columns:
            raise ValueError(f"'close' column not found in the DataFrame for {timeframe}.")

        df = indicators_data.copy()

        # Calculating Fibonacci retracement levels
        max_price = df['close'].rolling(window=self.fibonacci_lookback_period).max()
        min_price = df['close'].rolling(window=self.fibonacci_lookback_period).min()

        df['fib_0'] = min_price
        df['fib_0.236'] = min_price + 0.236 * (max_price - min_price)
        df['fib_0.382'] = min_price + 0.382 * (max_price - min_price)
        df['fib_0.5'] = min_price + 0.5 * (max_price - min_price)
        df['fib_0.618'] = min_price + 0.618 * (max_price - min_price)
        df['fib_0.786'] = min_price + 0.786 * (max_price - min_price)
        df['fib_1'] = max_price

        indicators_data = df
        return indicators_data

    def calculate_ATR(self, timeframe, indicators_data):
        high_prices = indicators_data["high"]
        low_prices = indicators_data["low"]
        close_prices = indicators_data["close"].shift(1)
        true_range = np.maximum(high_prices - low_prices, np.abs(high_prices - close_prices), np.abs(low_prices - close_prices))
        atr = true_range.rolling(window=14).mean().fillna(method='bfill')
        indicators_data["atr"] = atr
        return indicators_data
