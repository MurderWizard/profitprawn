import ccxt
import json

# Load API keys from a JSON file
with open('config.json') as json_file:
    config = json.load(json_file)

exchange = ccxt.phemex({
    'apiKey': config['api_key'],
    'secret': config['api_secret'],
})

symbol = 'BTC/USD:BTC'
funding_rate = exchange.fetch_funding_rate(symbol)
print(funding_rate)
