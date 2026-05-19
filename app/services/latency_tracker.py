from time import perf_counter


class LatencyTracker:
    def __init__(self):
        self.started_at = perf_counter()
        self.last_mark = self.started_at
        self.timings = {}

    def mark(self, name: str):
        now = perf_counter()
        self.timings[name] = round((now - self.last_mark) * 1000, 2)
        self.last_mark = now

    def set_elapsed(self, name: str, started_at: float):
        self.timings[name] = round((perf_counter() - started_at) * 1000, 2)

    def total(self):
        self.timings["total"] = round((perf_counter() - self.started_at) * 1000, 2)
        return self.timings
