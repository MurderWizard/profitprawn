import ccxt
import requests
import time
import hmac
import json
from datetime import datetime, timedelta

class FundingRateFetcher:
    def __init__(self):
        with open('config.json') as json_file:
            self.config = json.load(json_file)

        self.exchange = ccxt.phemex({
            'apiKey': self.config['api_key'],
            'secret': self.config['api_secret'],
        })

    def get_current_funding_rate(self):
        symbol = 'BTCUSD'
        try:
            funding_rate = self.exchange.fetch_funding_rate(symbol)
            return funding_rate['fundingRate']
        except Exception as e:
            print(f"Error getting current funding rate: {e}")
            return None




# Example usage
fetcher = FundingRateFetcher()

# Get current funding rate
current_rate = fetcher.get_current_funding_rate()
print(f"Current funding rate for BTCUSD: {current_rate}")

# Get historical funding rates for each day up to a week back
for i in range(7):
    date = datetime.now() - timedelta(days=i)
    historical_rates = fetcher.get_historical_funding_rates(date=date)
    print(f"Historical funding rates for {date.strftime('%Y-%m-%d')}: {historical_rates}")
