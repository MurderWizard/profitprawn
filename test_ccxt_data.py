import ccxt
import json

def fetch_single_candle_data(symbol, timeframe='1m', limit=1):
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

    bars = phemex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    return bars

# Define the symbol and timeframe for which you want to fetch the data
symbol = 'BTC/USD:BTC'
timeframe = '1d'
limit = 1

# Fetch a single candle data
candle_data = fetch_single_candle_data(symbol, timeframe, limit)
print(candle_data)
