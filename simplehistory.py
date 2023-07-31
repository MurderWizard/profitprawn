import ccxt
import pandas as pd
import json

# Load the API key and secret from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

api_key = config['api_key']
api_secret = config['api_secret']

phemex = ccxt.phemex({
    'enableRateLimit': True,
    'apiKey': api_key,
    'secret': api_secret
})

symbol = 'BTC/USD:BTC'  # Don't forget to quote the symbol correctly
timeframe = '1d'
limit = 500

bars = phemex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

print(df)
