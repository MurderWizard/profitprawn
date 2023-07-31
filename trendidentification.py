import pandas as pd


class TrendIdentification:
    def __init__(self, data_processor, vwma_short_period='30m', vwma_long_period='1w',
                 fibo_levels=[0.236, 0.382, 0.5, 0.618, 1.0], rsi_threshold=70):
        self.data_processor = data_processor
        self.vwma_short_period = vwma_short_period
        self.vwma_long_period = vwma_long_period
        self.fibo_levels = fibo_levels
        self.rsi_threshold = rsi_threshold

    def identify_trend_vwma_fibonacci_rsi(self, processed_data, indicators):
        if processed_data is None or not isinstance(processed_data, pd.DataFrame):
            print("Invalid processed data format. Please provide a Pandas DataFrame.")
            return None

        if indicators is None or not isinstance(indicators, pd.DataFrame):
            print("Invalid indicators format. Please provide a Pandas DataFrame.")
            return None

        # Exclude rows with NaN values
        processed_data = processed_data.dropna()
        indicators = indicators.dropna()

        trend_data = processed_data[['time', 'close']].copy()
        trend_data['trend'] = 'neutral'

        # Calculate VWMA and Fibonacci levels for the specified intervals
        vwma_short = self.data_processor.calculate_VWMA(processed_data, self.vwma_short_period)
        vwma_long = self.data_processor.calculate_weighted_vwma(processed_data, self.vwma_long_period)
        fibonacci_levels = self.data_processor.calculate_fibonacci_levels(processed_data, self.fibo_levels)

        # Check if the close price is above both the VWMA, weighted VWMA, and Fibonacci levels for a bullish trend
        bullish_conditions = (
            (processed_data['close'] > vwma_short) &
            (processed_data['close'] > vwma_long) &
            all(processed_data['close'] > level for level in fibonacci_levels) &
            (indicators['rsi'] < self.rsi_threshold)
        )

        trend_data.loc[bullish_conditions, 'trend'] = 'bullish'

        # Check if the close price is below both the VWMA, weighted VWMA, and Fibonacci levels for a bearish trend
        bearish_conditions = (
            (processed_data['close'] < vwma_short) &
            (processed_data['close'] < vwma_long) &
            all(processed_data['close'] < level for level in fibonacci_levels) &
            (indicators['rsi'] > self.rsi_threshold)
        )

        trend_data.loc[bearish_conditions, 'trend'] = 'bearish'

        return trend_data
