from collections import defaultdict, deque
from time import time


class InMemoryRateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)

    def check(self, *, key: str, limit: int, window_seconds: int = 60):
        now = time()
        bucket = self.requests[key]

        while bucket and bucket[0] <= now - window_seconds:
            bucket.popleft()

        remaining = max(limit - len(bucket), 0)

        if len(bucket) >= limit:
            retry_after = int(window_seconds - (now - bucket[0])) if bucket else window_seconds
            return {
                "allowed": False,
                "limit": limit,
                "remaining": 0,
                "retry_after": max(retry_after, 1),
            }

        bucket.append(now)

        return {
            "allowed": True,
            "limit": limit,
            "remaining": max(limit - len(bucket), 0),
            "retry_after": 0,
        }


rate_limiter = InMemoryRateLimiter()
