import datetime
from pytz import timezone
import pandas as pd
from historical_data_collection import HistoricalDataCollection

def test_historical_data_collection():
    utc = timezone('UTC')  # Define timezone
    symbol = 'BTC/USD:BTC'  # Add your symbol
    start_time = datetime.datetime(2023, 7, 15, 0, 0, tzinfo=utc)  # start_time is 7 days ago from current_time
    intervals = ['1m', '5m', '15m', '1h', '4h', '1d']  # Add your intervals

    # Instantiate HistoricalDataCollection
    hdc = HistoricalDataCollection(symbol=symbol)

    summary = {}  # Dictionary to store the summary for each interval
    debug_info = {}  # Dictionary to store debug information

    output = []  # List to store output

    for interval in intervals:
        # Fetch historical data for the interval
        data = hdc.get_historical_data(interval, start_time, num_periods=100)

        # If data is empty, add a message to the output list and continue to the next interval
        if data.empty:
            output.append(f"\nNo data fetched for {interval} interval.")
            summary[interval] = "No data fetched"
            debug_info[interval] = "No data fetched"
            continue

        # Add the first few rows of the data to the output list
        output.append(f"\nData for {interval} interval:")
        output.append(data.head().to_string())
        debug_info[interval] = data.head().to_dict()

        # Calculate and add the time difference between the requested and actual start times to the output list
        actual_start_time = data.index[0].tz_localize(utc)  # Make actual_start_time tz-aware
        time_difference = actual_start_time - start_time
        output.append(f"\nRequested start time: {start_time}")
        output.append(f"Actual start time: {actual_start_time}")
        output.append(f"Time difference: {time_difference}")

        # Add the details to the summary
        summary[interval] = {
            "requested_start_time": start_time,
            "actual_start_time": actual_start_time,
            "time_difference": time_difference
        }

    # Add the summary to the output list
    output.append("\nSummary:")
    for interval, details in summary.items():
        output.append(f"\nInterval: {interval}")
        if isinstance(details, str):
            output.append(details)
        else:
            output.append(f"Requested start time: {details['requested_start_time']}")
            output.append(f"Actual start time: {details['actual_start_time']}")
            output.append(f"Time difference: {details['time_difference']}")

    # Add the debug information to the output list
    output.append("\nDebug Information:")
    for interval, info in debug_info.items():
        output.append(f"\nInterval: {interval}")
        output.append(str(info))

    # Print the output
    print('\n'.join(output))


if __name__ == "__main__":
    test_historical_data_collection()
