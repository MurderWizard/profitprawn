import pandas as pd
from datetime import datetime
from historical_data_collection import HistoricalDataCollection
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class RawDataTester:
    def __init__(self, raw_data_dict):
        self.raw_data_dict = raw_data_dict
        self.timeframes = sorted(raw_data_dict.keys())
        self.test_results = {tf: {} for tf in self.timeframes}

    def test_data(self):
        for tf in self.timeframes:
            print(f"\nTesting raw data for {tf} interval...")

            if tf not in self.raw_data_dict:
                print(f"Error: Data for {tf} not found.")
                self.test_results[tf]['Error'] = f"Data for {tf} not found."
                continue

            raw_data_df = self.raw_data_dict[tf]

            # Check if data is empty
            if raw_data_df.empty:
                print(f"Error: Data for {tf} is empty.")
                self.test_results[tf]['Error'] = f"Data for {tf} is empty."
                continue

            # Check for required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = set(required_columns) - set(raw_data_df.columns)
            if missing_columns:
                print(f"Error: Data for {tf} is missing the following columns: {', '.join(missing_columns)}")
                self.test_results[tf]['Missing Columns'] = missing_columns
                continue

            # Check for incorrect data types
            incorrect_dtype_columns = [column for column in required_columns if
                                       raw_data_df[column].dtype not in ['int64', 'float64']]
            if incorrect_dtype_columns:
                print(
                    f"Error: Data for {tf} has incorrect data types for the following columns: {', '.join(incorrect_dtype_columns)}")
                self.test_results[tf]['Incorrect Data Types'] = incorrect_dtype_columns
                continue

            # Check for missing values
            if raw_data_df.isnull().values.any():
                print(f"Error: Data for {tf} contains NaN values.")
                nan_rows_columns = [(index, column) for index, row in raw_data_df.iterrows() for column in row.index if
                                    pd.isnull(row[column])]
                print(f"Rows and columns with NaN values in {tf} data:")
                for index, column in nan_rows_columns:
                    print(f"Row: {index}, Column: {column}")
                self.test_results[tf]['NaN Values'] = True
                continue

            # Check for duplicate timestamps
            duplicate_timestamps = raw_data_df.index[raw_data_df.index.duplicated()]
            if duplicate_timestamps.to_numpy().any():
                print(f"Error: Duplicate timestamps found in {tf} interval:")
                print(raw_data_df.loc[duplicate_timestamps])
                self.test_results[tf]['Duplicate Timestamps'] = True
                continue

            print(f"Data for {tf} interval passed all checks.")
            self.test_results[tf]['Passed'] = True

    def print_test_summary(self):
        print("\nTest Summary:")
        for tf, results in self.test_results.items():
            print(f"\n{tf} interval:")
            for test, result in results.items():
                print(f"{test}: {result}")


if __name__ == "__main__":
    # Create an instance of the HistoricalDataCollection class
    collector = HistoricalDataCollection(symbol='BTC/USD:BTC')

    # Define the start and end times for data collection
    end_time = datetime.now()
    start_time = end_time - timedelta(weeks=52)  # One year ago

    # Define the intervals for data collection
    intervals = ['1m', '1h', '1d', '1w', '1M']

    # Define the number of periods for each interval
    num_periods_dict = {
        '1m': 60,  # 1 hour worth of 1m data
        '1h': 24,  # 24 hours worth of 1h data
        '1d': 7,   # 7 days worth of 1d data
        '1w': 4,   # 1 month worth of 1w data (assuming a month is about 4 weeks)
        '1M': 3    # 3 months worth of 1M data
    }

    # Fetch the raw data
    raw_data_dict = {}
    for interval in intervals:
        num_periods = num_periods_dict[interval]
        raw_data_dict[interval] = collector.get_historical_data(interval, start_time, num_periods)

    # Create an instance of the RawDataTester class
    tester = RawDataTester(raw_data_dict)

    # Run the tests on the raw data
    tester.test_data()

    # Print the test summary
    tester.print_test_summary()
