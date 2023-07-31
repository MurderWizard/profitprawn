import ccxt
import json

class PhemexDataFetcher:
    def __init__(self, config_file='config.json'):
        with open(config_file) as f:
            config = json.load(f)
        self.exchange = ccxt.phemex({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'enableRateLimit': True
        })

    def fetch_trading_pair_symbols(self):
        try:
            markets = self.exchange.fetch_markets()
            symbols = [market['symbol'] for market in markets]
            return symbols
        except ccxt.ExchangeError as e:
            print(f"Error fetching trading pair symbols: {e}")
            return []

    def fetch_time_frames(self):
        try:
            return self.exchange.timeframes
        except ccxt.ExchangeError as e:
            print(f"Error fetching time frames: {e}")
            return []

    def fetch_funding_rate(self, symbol):
        try:
            funding_rate_info = self.exchange.fetch_funding_rate(symbol)
            return funding_rate_info
        except ccxt.ExchangeError as e:
            print(f"Error fetching funding rate: {e}")
            return None

# Create a PhemexDataFetcher instance
data_fetcher = PhemexDataFetcher()

# Fetch trading pair symbols and print them
symbols = data_fetcher.fetch_trading_pair_symbols()
print("Trading pair symbols:")
for symbol in symbols:
    print(symbol)

# Fetch time frames and print them
time_frames = data_fetcher.fetch_time_frames()
print("\nTime frames:")
for time_frame in time_frames:
    print(time_frame)

# Fetch funding rate for each symbol and print it
print("\nFunding rates:")
for symbol in symbols:
    if symbol.endswith('USD'):  # Only fetch funding rate for perpetual futures contracts
        funding_rate_info = data_fetcher.fetch_funding_rate(symbol)
        print(f"For {symbol}: {funding_rate_info}")
