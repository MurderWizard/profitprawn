import pandas as pd
import numpy as np

class SupportResistance:
    def __init__(self, data, margin=0.02, window_size=10, lookback_period=24):
        self.data = data
        self.margin = margin
        self.window_size = window_size
        self.lookback_period = lookback_period

    def calculate_average_true_range(self):
        high = self.data['high']
        low = self.data['low']
        close_prev = self.data['close'].shift(1)
        true_range = np.maximum(high - low, np.abs(high - close_prev), np.abs(low - close_prev))
        atr = true_range.rolling(window=self.window_size).mean().fillna(method='bfill')
        return atr

    def identify_support_resistance(self):
        if self.data is None or not isinstance(self.data, pd.DataFrame):
            print("Invalid data format. Please provide a Pandas DataFrame.")
            return None

        self.data = self.data.interpolate()

        support_resistance_data = pd.DataFrame(index=self.data.index)

        support_resistance_data['support_level'] = self.data['low'].rolling(window=self.window_size, center=True).min().fillna(method='bfill')
        support_resistance_data['resistance_level'] = self.data['high'].rolling(window=self.window_size, center=True).max().fillna(method='bfill')

        support_resistance_data['support_level'] = np.minimum(support_resistance_data['support_level'], self.data['low'].rolling(window=self.lookback_period).min())
        support_resistance_data['resistance_level'] = np.maximum(support_resistance_data['resistance_level'], self.data['high'].rolling(window=self.lookback_period).max())

        rolling_mean = self.data['close'].rolling(window=self.window_size).mean()
        rolling_std = self.data['close'].rolling(window=self.window_size).std()
        support_resistance_data['support_level'] = np.minimum(support_resistance_data['support_level'], rolling_mean - 2 * rolling_std)
        support_resistance_data['resistance_level'] = np.maximum(support_resistance_data['resistance_level'], rolling_mean + 2 * rolling_std)

        rolling_max = self.data['high'].rolling(window=self.window_size).max()
        rolling_min = self.data['low'].rolling(window=self.window_size).min()
        support_resistance_data['support_level'] = np.minimum(support_resistance_data['support_level'], rolling_min)
        support_resistance_data['resistance_level'] = np.maximum(support_resistance_data['resistance_level'], rolling_max)

        atr = self.calculate_average_true_range()
        support_resistance_data['support_level'] = np.minimum(support_resistance_data['support_level'], rolling_mean - 2 * atr)
        support_resistance_data['resistance_level'] = np.maximum(support_resistance_data['resistance_level'], rolling_mean + 2 * atr)

        support_resistance_data['support_level'] = support_resistance_data['support_level'] * (1 - self.margin)
        support_resistance_data['resistance_level'] = support_resistance_data['resistance_level'] * (1 + self.margin)

        support_resistance_data = support_resistance_data.dropna()

        return support_resistance_data
