import websocket
from datetime import datetime
import json
import pandas as pd
import time
import os

class RealTimeDataCollection:
    def __init__(self):
        self.df = pd.DataFrame(columns=["timestamp", "price", "volume"])
        self.ws = websocket.WebSocketApp("wss://phemex.com/ws",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_ping=self.on_ping,
                                         on_pong=self.on_pong)
        self.is_closed = False
        self.error = None

    def on_open(self, ws):
        print("Connection opened")
        symbols = ["trade.BTCUSDT", "trade.ETHUSDT", "trade.XRPUSDT"]  # Add more trading pairs if needed
        timeframes = ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M", "1Y"]  # All available timeframes
        for symbol in symbols:
            for timeframe in timeframes:
                ws.send(json.dumps({
                    "op": "subscribe",
                    "args": [f"{symbol}.{timeframe}"]
                }))

    def on_message(self, ws, message):
        data = json.loads(message)
        if "table" in data and data["table"] == "trade":
            for trade in data["data"]:
                timestamp = datetime.fromtimestamp(trade["timestamp"] / 1000)
                price = float(trade["price"])
                volume = float(trade["size"])
                self.df.loc[len(self.df)] = [timestamp, price, volume]

    def on_error(self, ws, error):
        print(f"Error: {error}")
        self.error = error

    def on_close(self, ws):
        print("Connection closed")
        self.is_closed = True

    def on_ping(self, ws, message):
        print("Ping received")

    def on_pong(self, ws, message):
        print("Pong received")

    def reconnect(self):
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                print(f"Exception: {e}. Reconnecting...")
                time.sleep(1)

    def start(self):
        self.reconnect()
