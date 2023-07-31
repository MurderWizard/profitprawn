import ccxt

exchange = ccxt.phemex()
exchange.load_markets()

# Get the available market symbols
market_symbols = exchange.symbols

print("Available market symbols on Phemex:", market_symbols)