import os
import tracemalloc

try:
    import psutil
except ImportError:  # psutil is optional: RSS is simply omitted
    psutil = None


def rss_mb():
    if psutil is None:
        return None
    return round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 2)


class MemoryProbe:
    """Context manager measuring peak Python allocations (tracemalloc) during a block."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.peak_kb = None
        self._was_tracing = False

    def __enter__(self):
        if self.enabled:
            self._was_tracing = tracemalloc.is_tracing()
            if not self._was_tracing:
                tracemalloc.start()
            tracemalloc.reset_peak()
        return self

    def __exit__(self, *exc):
        if self.enabled:
            self.peak_kb = round(tracemalloc.get_traced_memory()[1] / 1024, 2)
            if not self._was_tracing:
                tracemalloc.stop()


def memory_block(probe, index_mb):
    if not probe.enabled:
        return None
    return {"peak_kb": probe.peak_kb, "index_mb": index_mb, "rss_mb": rss_mb()}
