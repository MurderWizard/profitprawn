import time
import ccxt
from datetime import datetime
from datacollection import RealTimeDataCollection
from dataprocessing import DataProcessing
from signalgeneration import SignalGeneration
from supportresistance import SupportResistance
from trendidentification import TrendIdentification
from riskmanagement import RiskManagement
from exemanage import TradeExecution


class MultiTimeframeTrendFollowingBot:
    def __init__(self, api_key, api_secret, trading_capital):
        self.data_collection = RealTimeDataCollection(api_key, api_secret)
        self.data_processing = DataProcessing()
        self.signal_generation = SignalGeneration()
        self.support_resistance = SupportResistance()
        self.trend_identification = TrendIdentification()
        self.risk_management = RiskManagement(trading_capital)
        self.trade_execution = TradeExecution(api_key, api_secret)

    def run(self):
        while True:
            try:
                # Collect and process data
                data = self.data_collection.collect_data('BTC/USD')
                data = self.data_processing.process_data(data)

                # Identify support and resistance
                self.support_resistance.identify_support_resistance(data)

                # Identify trend
                self.trend_identification.identify_trend(data)

                # Generate signals
                self.signal_generation.generate_signals(data)

                # Manage risk
                self.risk_management.calculate_position_size(data)
                self.risk_management.calculate_stop_loss(data)
                self.risk_management.calculate_take_profit(data)

                # Execute trades
                signal = data['Signal'].iloc[-1]
                symbol = 'BTC/USD'
                price = data['Close'].iloc[-1]
                stop_loss = data['Stop_Loss'].iloc[-1]
                take_profit = data['Take_Profit'].iloc[-1]
                self.trade_execution.manage_trade(signal, symbol, price, stop_loss, take_profit)

                print(f"{datetime.now()}: Successfully executed trading loop.")
            except Exception as e:
                print(f"{datetime.now()}: Encountered an error during the trading loop: {e}")

            # Sleep for 5 minutes
            time.sleep(5 * 60)
