from time import perf_counter

from app.services.latency_tracker import LatencyTracker


def test_latency_tracker_total_returns_dict():
    tracker = LatencyTracker()
    result = tracker.total()

    assert "total" in result
    assert result["total"] >= 0


def test_latency_tracker_set_elapsed():
    tracker = LatencyTracker()
    started = perf_counter()
    tracker.set_elapsed("stage", started)

    assert "stage" in tracker.timings
    assert tracker.timings["stage"] >= 0
