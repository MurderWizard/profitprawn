import ccxt
import os


class TradeExecution:
    def __init__(self, api_key, api_secret):
        self.exchange = ccxt.phemex({
            'apiKey': api_key,
            'secret': api_secret
        })
        self.taker_fee = 0.00075  # Taker fee for BTC/USD contracts
        self.maker_fee = -0.00025  # Maker fee for BTC/USD contracts
        self.open_order = None

    def execute_trade(self, signal, symbol, price, stop_loss, take_profit):
        # Check if the signal is a buy signal
        if signal > 0:
            # Place a buy order
            order = self.exchange.create_market_buy_order(symbol, signal)
            fee = self.taker_fee  # Assume taker fee for market orders
        elif signal < 0:
            # Place a sell order
            order = self.exchange.create_market_sell_order(symbol, -signal)
            fee = self.taker_fee  # Assume taker fee for market orders

        # Adjust the stop loss and take profit levels to account for fees
        stop_loss = stop_loss * (1 + fee) if signal > 0 else stop_loss * (1 - fee)
        take_profit = take_profit * (1 - fee) if signal > 0 else take_profit * (1 + fee)

        # Save the order ID for later reference
        self.open_order = order['id']

    def simulate_trade(self, signal, price, stop_loss, take_profit):
        # Simulate the execution of a trade
        if signal > 0:
            # Simulate a buy order
            if price <= stop_loss:
                return -self.balance * self.taker_fee
            elif price >= take_profit:
                return self.balance * self.taker_fee
            else:
                return 0
        elif signal < 0:
            # Simulate a sell order
            if price >= stop_loss:
                return -self.balance * self.taker_fee
            elif price <= take_profit:
                return self.balance * self.taker_fee
            else:
                return 0

    def check_balance(self):
        # Fetch the balance from the exchange
        balance = self.exchange.fetch_balance()
        return balance['free']['BTC']

    def calculate_position_size(self, risk_management):
        # Calculate the position size based on the risk management rules
        balance = self.check_balance()
        position_size = balance * risk_management.risk_per_trade
        return position_size

    def get_open_order(self):
        # Fetch the current open order
        if self.open_order:
            order = self.exchange.fetch_order(self.open_order)
            return order
        else:
            return None

    def manage_trade(self, signal, symbol, price, stop_loss, take_profit, threshold=0.5):
        # Fetch the current open order
        order = self.get_open_order()

        # If there is an open order and we have a signal in the opposite direction or the signal strength drops below the threshold, close the open order and execute a new trade if the signal strength is above the threshold
        if order and ((signal > 0 and order['side'] == 'sell') or (signal < 0 and order['side'] == 'buy') or abs(signal) < threshold):
            self.exchange.cancel_order(order['id'])
            self.open_order = None  # Reset the open order
            if abs(signal) > threshold:
                self.execute_trade(signal, symbol, price, stop_loss, take_profit)
        # If there is no open order and we have a signal, execute a new trade
        elif not order and abs(signal) > threshold:
            self.execute_trade(signal, symbol, price, stop_loss, take_profit)


class MockTradeExecution(TradeExecution):
    def __init__(self, api_key, api_secret):
        super().__init__(api_key, api_secret)
        self.balance = 1.0  # Initial balance in BTC

    def execute_trade(self, signal, symbol, price, stop_loss, take_profit):
        # Simulate the execution of a trade
        if signal > 0:
            # Simulate a buy order
            self.balance -= price * signal
            fee = self.taker_fee  # Assume taker fee for market orders
        elif signal < 0:
            # Simulate a sell order
            self.balance += price * -signal
            fee = self.taker_fee  # Assume taker fee for market orders

        # Adjust the stop loss and take profit levels to account for fees
        stop_loss = stop_loss * (1 + fee) if signal > 0 else stop_loss * (1 - fee)
        take_profit = take_profit * (1 - fee) if signal > 0 else take_profit * (1 + fee)

        # Save the order ID for later reference
        self.open_order = os.urandom(16).hex()  # Generate a random order ID

    def check_balance(self):
        # Return the simulated balance
        return self.balance

    def get_open_order(self):
        # Return a simulated open order
        return {'id': self.open_order, 'side': 'buy' if self.balance > 0 else 'sell'} if self.open_order else None

    def manage_trade(self, signal, symbol, price, stop_loss, take_profit, threshold=0.5):
        # Simulate the management of a trade
        order = self.get_open_order()

        # If there is an open order and we have a signal in the opposite direction or the signal strength drops below the threshold, close the open order and execute a new trade if the signal strength is above the threshold
        if order and ((signal > 0 and order['side'] == 'sell') or (signal < 0 and order['side'] == 'buy') or abs(signal) < threshold):
            self.open_order = None  # Reset the open order
            if abs(signal) > threshold:
                self.execute_trade(signal, symbol, price, stop_loss, take_profit)
        # If there is no open order and we have a signal, execute a new trade
        elif not order and abs(signal) > threshold:
            self.execute_trade(signal, symbol, price, stop_loss, take_profit)
