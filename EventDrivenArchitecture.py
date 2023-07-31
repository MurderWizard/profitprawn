class Event:
    def __init__(self):
        self._subscribers = set()

    def subscribe(self, who):
        self._subscribers.add(who)

    def unsubscribe(self, who):
        self._subscribers.discard(who)

    def emit(self, what):
        for subscriber in self._subscribers:
            subscriber(what)


class DataHandler:
    def __init__(self, event):
        self.event = event
        self.event.subscribe(self.handle_event)

    def handle_event(self, data):
        print(f"DataHandler received data: {data}")
