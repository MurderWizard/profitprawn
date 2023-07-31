import pandas as pd
from EventDrivenArchitecture import Event

class DataProcessing:
    def __init__(self, event=None):
        self.raw_data_dict = {}
        self.timeframes = []
        self.processed_data = {}
        if event:
            event.subscribe(self.process_data_event)

    def process_data_event(self, data):
        # Here, data is the DataFrame emitted by the HistoricalDataCollection class
        # You can now process this data
        print(f"DataProcessing received data: {data}")

        # Assuming the data is for a single timeframe
        # Extract the timeframe from the data
        timeframe = data.index.to_series().diff().mode()[0].components.hours

        # Store the raw data
        self.raw_data_dict[timeframe] = data
        self.timeframes.append(timeframe)

        # Process the data
        start_time = data.index.min()  # Assuming the DataFrame is indexed by timestamp
        stop_on_irregular_frequency = True  # You can adjust this as needed
        processed_data = self.process_data(str(timeframe) + 'h', start_time, stop_on_irregular_frequency)

        # Store the processed data
        self.processed_data[timeframe] = processed_data

        print(f"Processed data for {timeframe} interval:")
        print(processed_data.head())

    def verify_input_data(self):
        for tf in self.timeframes:
            if tf not in self.raw_data_dict:
                raise ValueError(f"Error: Data for {tf} not found in input data.")
            data = self.raw_data_dict[tf]
            if not isinstance(data, pd.DataFrame):
                raise ValueError(f"Error: Data for {tf} is not a DataFrame.")
            if not isinstance(data.index, pd.DatetimeIndex):
                raise ValueError(f"Error: Index for {tf} data is not a DatetimeIndex.")
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = set(required_columns) - set(data.columns)
            if missing_columns:
                raise ValueError(f"Error: Data for {tf} is missing the following columns: {', '.join(missing_columns)}")
        print("Input data verification passed.")

    def check_data(self, data, timeframe):
        print(f"\nChecking data for {timeframe} interval...")

        if data.empty:
            print(f"No data available for {timeframe} interval.")
            return False

        # Check for duplicate timestamps
        duplicate_timestamps = data.index[data.index.duplicated()]
        if duplicate_timestamps.to_numpy().any():
            print(f"Duplicate timestamps found in {timeframe} interval:")
            print(data.loc[duplicate_timestamps])
            return False

        # Check for irregular frequency
        time_diff = data.index.to_series().diff()
        time_diff = pd.to_timedelta(time_diff)  # Convert time_diff to Timedelta
        tolerance = pd.Timedelta(seconds=0.5)  # Tolerance for the time difference
        expected_time_diff = pd.Timedelta(minutes=1) if timeframe == '1m' else \
            pd.Timedelta(hours=1) if timeframe == '1h' else \
                pd.Timedelta(days=1) if timeframe == '1d' else \
                    pd.Timedelta(weeks=1) if timeframe == '1w' else \
                        pd.Timedelta(days=30)  # Assuming a month is 30 days
        irregular_frequency = (
                (time_diff < expected_time_diff - tolerance) | (time_diff > expected_time_diff + tolerance)).any()
        if irregular_frequency:
            print(f"Irregular frequency found in {timeframe} interval.")
            print(
                data.index[(time_diff < expected_time_diff - tolerance) | (time_diff > expected_time_diff + tolerance)])
            return False

        print(f"Data type of timestamps in {timeframe} data after conversion:")
        print(data.index.dtype)

        return True

    def process_data(self, interval, start_time, stop_on_irregular_frequency=False):
        print(f"\nProcessing data for {interval} interval...")

        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if interval not in self.raw_data_dict:
            print(f"Error: Data for {interval} not found.")
            return pd.DataFrame()

        raw_data_df = self.raw_data_dict[interval]

        print(f"\nRaw data for {interval} interval right after fetch:")
        print(raw_data_df.head())

        missing_columns = set(required_columns) - set(raw_data_df.columns)
        if missing_columns:
            print(f"Error: Columns {', '.join(missing_columns)} not found in the {interval} data.")
            return pd.DataFrame()

        print(f"\nData for {interval} interval after checking for missing columns:")
        print(raw_data_df.head())

        # Ensure the data types are correct
        for column in required_columns:
            raw_data_df[column] = pd.to_numeric(raw_data_df[column], errors='coerce')

        print(f"\nData types for 'open', 'high', 'low', 'close', and 'volume' columns in {interval} data:")
        for column in ['open', 'high', 'low', 'close', 'volume']:
            print(f"{column}: {raw_data_df[column].dtype}")

        incorrect_dtype_columns = [column for column in required_columns if
                                   raw_data_df[column].dtype not in ['int64', 'float64']]
        if incorrect_dtype_columns:
            print(
                f"Error: Data for {interval} has incorrect data types for the following columns: {', '.join(incorrect_dtype_columns)}.")
            return pd.DataFrame()

        print(f"\nData for {interval} interval after checking for incorrect data types:")
        print(raw_data_df.head())

        if raw_data_df.isnull().values.any():
            print(f"Error: Data for {interval} contains NaN values.")
            nan_rows_columns = [(index, column) for index, row in raw_data_df.iterrows() for column in row.index if
                                pd.isnull(row[column])]
            print(f"Rows and columns with NaN values in {interval} data:")
            for index, column in nan_rows_columns:
                print(f"Row: {index}, Column: {column}")
            return pd.DataFrame()

        print(f"\nData for {interval} interval after checking for NaN values:")
        print(raw_data_df.head())

        # Filter data based on start_time
        print(f"Start time before filtering: {start_time}, Type: {type(start_time)}")
        start_time = start_time.replace(tzinfo=None)
        print(f"Start time after removing timezone: {start_time}, Type: {type(start_time)}")
        raw_data_df = raw_data_df[raw_data_df.index.tz_localize(None) >= start_time]

        processed_data = raw_data_df.copy()
        is_data_valid = self.check_data(processed_data, interval)

        if not is_data_valid:
            print(f"Warning: Data for {interval} interval has irregular frequency.")
            if stop_on_irregular_frequency:
                print(f"Data for {interval} could not be processed due to errors.")
                return pd.DataFrame()

        print(
            f"Processed data for {interval} interval has {processed_data.shape[0]} rows and {processed_data.shape[1]} columns.")
        print(f"Processed data for {interval} interval:")
        print(processed_data.head())

        self.processed_data[interval] = processed_data

        return processed_data

    def get_processed_data(self):
        if not self.processed_data:
            print("No processed data available.")
            return self.processed_data

        # Call process_data method for each timeframe
        for tf in self.timeframes:
            start_time = self.raw_data_dict[tf].index.min()  # Assuming the DataFrame is indexed by timestamp
            stop_on_irregular_frequency = True  # You can adjust this as needed
            self.processed_data[tf] = self.process_data(tf, start_time, stop_on_irregular_frequency)

        return self.processed_data
