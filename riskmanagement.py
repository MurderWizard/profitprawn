# Risk of the trade diveded by the equity of the trade, we should look into that.



import numpy as np

class RiskManagement:
    def __init__(self, trading_capital, risk_per_trade=0.03, risk_reward_ratio=2, **kwargs):
        self.trading_capital = trading_capital
        self.risk_per_trade = risk_per_trade
        self.risk_reward_ratio = risk_reward_ratio
        self.support_columns = kwargs.get('support_columns', ['low'])
        self.resistance_columns = kwargs.get('resistance_columns', ['high'])

    def calculate_stop_loss(self, processed_data, indicators_data, support_resistance_data):
        # Check if the required columns exist in the processed_data, indicators_data, and support_resistance_data
        required_columns = ['macd', 'macd_signal', 'vwma', 'dc_high', 'kc_high', 'support_level']
        missing_columns = set(required_columns) - set(processed_data.columns) - set(indicators_data.columns) - set(
            support_resistance_data.columns)

        if missing_columns:
            print(f"Error: Columns {', '.join(missing_columns)} not found in the data.")
            return None

        # Calculate the stop loss based on the conditions and indicators
        processed_data['stop_loss'] = np.where(
            (processed_data['close'] > support_resistance_data['support_level']) &
            (indicators_data['macd'] > indicators_data['macd_signal']) &
            (processed_data['close'] > indicators_data['vwma']) &
            (processed_data['close'] > indicators_data['dc_high']) &
            (processed_data['close'] > indicators_data['kc_high']),
            indicators_data['kc_low'],
            indicators_data['kc_high']
        )

        return processed_data



    def calculate_position_size(self, processed_data, indicators_data, signals_data):
        # Check if the required columns exist in the processed_data, indicators_data, and signals_data
        required_columns = ['support_level', 'macd', 'macd_signal', 'vwma', 'dc_high', 'kc_high']
        missing_columns = set(required_columns) - set(processed_data.columns) - set(indicators_data.columns)

        if missing_columns:
            print(f"Error: Columns {', '.join(missing_columns)} not found in the data.")
            return None

        # Calculate the position size based on the risk per trade and the distance to the stop loss
        processed_data['position_size'] = (self.trading_capital * self.risk_per_trade) / (
                processed_data['close'] - processed_data['stop_loss'])

    def calculate_take_profit(self, processed_data, support_data, resistance_data):
        # Check if the required columns exist in the processed_data
        required_columns = ['close', 'stop_loss']
        missing_columns = set(required_columns) - set(processed_data.columns)

        if missing_columns:
            print(f"Error: Columns {', '.join(missing_columns)} not found in the data.")
            return None

        # Calculate the take profit based on the risk reward ratio and the stop loss
        processed_data['take_profit'] = processed_data['close'] + self.risk_reward_ratio * (
                processed_data['close'] - processed_data['stop_loss'])

        return processed_data

    def calculate_drawdown(self, processed_data):
        # Check if the required columns exist in the processed_data
        required_columns = ['close', 'support_level']
        missing_columns = set(required_columns) - set(processed_data.columns)

        if missing_columns:
            print(f"Error: Columns {', '.join(missing_columns)} not found in the data.")
            return None

        processed_data['drawdown'] = (processed_data['close'] - processed_data['support_level']) / processed_data['support_level']

    def identify_weak_trend(self, processed_data):
        # Identify when the trend might be weakening
        processed_data['weak_trend'] = (
            (processed_data['macd'] < processed_data['macd_signal']) & (processed_data['close'] < processed_data['vwma'])
        ) | (
            (processed_data['macd'] > processed_data['macd_signal']) & (processed_data['close'] > processed_data['vwma'])
        )

    def adjust_stop_loss(self, processed_data):
        # Adjust the stop loss to the breakeven point when the price has moved in our favor by the distance to the stop loss
        processed_data['stop_loss'] = np.where(
            (processed_data['signal'] > 0) & (processed_data['close'] - processed_data['entry_price'] > processed_data['entry_price'] - processed_data['stop_loss']),
            processed_data['entry_price'],
            processed_data['stop_loss']
        )
        processed_data['stop_loss'] = np.where(
            (processed_data['signal'] < 0) & (processed_data['entry_price'] - processed_data['close'] > processed_data['stop_loss'] - processed_data['entry_price']),
            processed_data['entry_price'],
            processed_data['stop_loss']
        )

    def adjust_take_profit(self, processed_data):
        # Adjust the take profit level when the trend is weakening
        processed_data['take_profit'] = np.where(processed_data['weak_trend'], processed_data['close'], processed_data['take_profit'])
