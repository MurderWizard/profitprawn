import datetime
from historical_data_collection import HistoricalDataCollection
class MaxPeriodsChecker:
    def __init__(self):
        self.historical_data_collector = HistoricalDataCollection()
        self.intervals = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w', '2w', '1M']
        self.start_time = datetime.datetime.now() - datetime.timedelta(days=5*365)  # 5 years ago

    def check_max_periods(self):
        max_periods_dict = {}
        for interval in self.intervals:
            print(f"Checking max periods for {interval} interval...")
            data = self.historical_data_collector.get_historical_data(interval, self.start_time)
            max_periods = len(data)
            max_periods_dict[interval] = max_periods
            print(f"Max periods for {interval} interval: {max_periods}")

        print("\nSummary of max periods for each interval:")
        for interval, max_periods in max_periods_dict.items():
            print(f"{interval}: {max_periods}")

if __name__ == "__main__":
    checker = MaxPeriodsChecker()
    checker.check_max_periods()


# Max Periods
# 5m: 1000
# 15m: 1000
# 30m: 1000
# 1h: 1000
# 2h: 1000
# 4h: 1000
# 6h: 1000
# 12h: 1000
# 1d: 1000
# 3d: 0
# 1w: 191
# 2w: 0
# 1M: 44