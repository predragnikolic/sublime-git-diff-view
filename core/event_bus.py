from typing import Dict, Callable


class Event:
    events = {}  # type: Dict[str, Callable[..., None]]

    @classmethod
    def listen(self, key, listener):
        if key in self.events:
            self.events[key].append(listener)
        else:
            self.events[key] = [listener]
        return lambda: self.removeListener(key, listener)

    @classmethod
    def removeListener(self, key, listener):
        if key in self.events:
            self.events[key].remove(listener)

    @classmethod
    def fire(self, key, *args):
        if key in self.events:
            for listener in self.events[key]:
                listener(*args)
