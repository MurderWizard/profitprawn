from datetime import datetime, timedelta
import pytz
from historical_data_collection import HistoricalDataCollection

def fetch_24_hours_data():
    # Set the symbol and interval for data retrieval
    symbol = 'BTC/USD:BTC'
    interval = '1m'

    # Get the current time in UTC
    end_time = datetime.now(pytz.utc)

    # Calculate the start time (24 hours ago) in UTC
    start_time = end_time - timedelta(days=1)

    # Make sure both current_time and end_time are in the UTC timezone
    start_time = start_time.replace(tzinfo=pytz.utc)
    end_time = end_time.replace(tzinfo=pytz.utc)

    # Create an instance of the HistoricalDataCollection class
    data_collector = HistoricalDataCollection()

    # Fetch historical 1-minute data for the past 24 hours
    df = data_collector.get_historical_data(interval, start_time, end_time, symbol=symbol)

    return df

# Fetch historical 1-minute data for the past 24 hours and print the result
data_24_hours = fetch_24_hours_data()
print(data_24_hours)
