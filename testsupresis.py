import pandas as pd
from datetime import datetime
from historical_data_collection import HistoricalDataCollection
from supportresistance import SupportResistance
import random

def check_nan_values(df):
    if df.isnull().values.any():
        nan_rows = df[df.isnull().any(axis=1)]
        print("Rows with NaN values:")
        print(nan_rows)
    else:
        print("No NaN values found in the DataFrame.")

collector = HistoricalDataCollection()

symbol = 'BTC/USD:BTC'
start_date = datetime(2023, 6, 1)
end_date = datetime(2023, 6, 15)
interval = '1h'

data = collector.get_historical_data(interval, start_date)

print("Checking raw data for NaN values:")
check_nan_values(data)

support_resistance = SupportResistance(data)

support_resistance_data = support_resistance.identify_support_resistance()

print("Checking support and resistance data for NaN values:")
check_nan_values(support_resistance_data)

print("Support and Resistance Data:")
print(support_resistance_data)

support_resistance_data = support_resistance_data.dropna()

random_hours = random.sample(list(support_resistance_data.index), 5)

for hour in random_hours:
    print(f"\nSupport and resistance levels for {hour}:")
    print(support_resistance_data.loc[hour])
