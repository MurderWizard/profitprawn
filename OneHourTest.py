from datetime import datetime, timedelta
from historical_data_collection import HistoricalDataCollection
from dataprocessing import DataProcessing

class DataVerificationModule:
    def __init__(self, data_collection):
        self.data_collection = data_collection

    def verify_data(self):
        try:
            raw_data_dict = self.data_collection.get_multi_timeframe_data(['1h'], start_time=datetime.now() - timedelta(weeks=1), end_time=datetime.now())
            print("Raw data dict:", raw_data_dict)
        except Exception as e:
            print("Error occurred during data collection: ", str(e))
            return

        data_processing = DataProcessing(raw_data_dict)

        interval = '1h'
        start_time = datetime.now() - timedelta(weeks=1)

        try:
            processed_data = data_processing.process_data(interval, start_time)
            print("Processed data: ", processed_data)
        except Exception as e:
            print("Error occurred during data processing: ", str(e))
            return

        print("Data verification passed.")


# Initialize the classes
data_collection = HistoricalDataCollection(symbol='BTC/USD:BTC')

# Create a DataVerificationModule object
data_verification_module = DataVerificationModule(data_collection)

# Call the verify_data method
data_verification_module.verify_data()
