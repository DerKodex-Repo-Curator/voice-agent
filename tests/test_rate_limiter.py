from app.services.rate_limiter import InMemoryRateLimiter


def test_rate_limiter_allows_until_limit():
    limiter = InMemoryRateLimiter()

    first = limiter.check(key="test-user", limit=2, window_seconds=60)
    second = limiter.check(key="test-user", limit=2, window_seconds=60)

    assert first["allowed"] is True
    assert second["allowed"] is True


def test_rate_limiter_blocks_after_limit():
    limiter = InMemoryRateLimiter()

    limiter.check(key="test-user", limit=1, window_seconds=60)
    blocked = limiter.check(key="test-user", limit=1, window_seconds=60)

    assert blocked["allowed"] is False
    assert blocked["retry_after"] >= 1
