import pandas as pd
import numpy as np

class SignalGeneration:
    def __init__(self, data, indicators_data, funding_rate=None, params=None):
        self.data = data
        self.indicators_data = indicators_data
        self.funding_rate = funding_rate

        # Set default parameters
        self.params = {
            'support_level_factor': 1,
            'macd_factor': 1,
            'vwma_factor': 1,
            'dc_high_factor': 1,
            'kc_high_factor': 1,
            'atr_factor': 2,
            'fib_buy_level_factor': 1,
            'funding_rate_buy_threshold': -0.001,  # Adjust this as per your strategy
            'resistance_level_factor': 1,
            'dc_low_factor': 1,
            'kc_low_factor': 1,
            'fib_sell_level_factor': 1,
            'funding_rate_sell_threshold': 0.001,  # Adjust this as per your strategy
            'min_buy_conditions': 3,
            'min_sell_conditions': 3
        }

        # If params are provided, update default parameters
        if params is not None:
            self.params.update(params)

    def generate_signals(self, trend_data):
        signals_data = pd.DataFrame(index=self.data.index)
        signals_data['signal'] = 'neutral'

        # Generate buy signals
        buy_conditions = [
            self.data['close'] > self.params['support_level_factor'] * self.indicators_data['support_level'],
            self.indicators_data['macd'] > self.params['macd_factor'] * self.indicators_data['macd_signal'],
            self.data['close'] > self.params['vwma_factor'] * self.indicators_data['vwma'],
            self.data['close'] > self.params['dc_high_factor'] * self.indicators_data['dc_high'],
            self.data['close'] > self.params['kc_high_factor'] * self.indicators_data['kc_high'],
            self.data['close'] - self.data['close'].shift() > self.params['atr_factor'] * self.indicators_data['atr'],
            self.data['close'] > self.params['fib_buy_level_factor'] * self.indicators_data['fib_0.382'],
            np.nan if self.funding_rate is None else self.funding_rate < self.params['funding_rate_buy_threshold']
        ]

        signals_data.loc[(trend_data['trend'] == 'uptrend') & (sum([x for x in buy_conditions if x is not np.nan]) >= self.params['min_buy_conditions']), 'signal'] = 'buy'

        # Generate sell signals
        sell_conditions = [
            self.data['close'] < self.params['resistance_level_factor'] * self.indicators_data['resistance_level'],
            self.indicators_data['macd'] < self.params['macd_factor'] * self.indicators_data['macd_signal'],
            self.data['close'] < self.params['vwma_factor'] * self.indicators_data['vwma'],
            self.data['close'] < self.params['dc_low_factor'] * self.indicators_data['dc_low'],
            self.data['close'] < self.params['kc_low_factor'] * self.indicators_data['kc_low'],
            self.data['close'].shift() - self.data['close'] > self.params['atr_factor'] * self.indicators_data['atr'],
            self.data['close'] < self.params['fib_sell_level_factor'] * self.indicators_data['fib_0.618'],
            np.nan if self.funding_rate is None else self.funding_rate > self.params['funding_rate_sell_threshold']
        ]

        signals_data.loc[(trend_data['trend'] == 'downtrend') & (sum([x for x in sell_conditions if x is not np.nan]) >= self.params['min_sell_conditions']), 'signal'] = 'sell'

        return signals_data
