"""
Application wide constants.

Centralizing constants reduces
magic numbers across modules.
"""

# Sliding Window Defaults

DEFAULT_REQUEST_LIMIT = 100

DEFAULT_WINDOW_SIZE_SECONDS = 1

WINDOW_TTL_MULTIPLIER = 2


# Token Bucket Defaults

DEFAULT_TOKEN_COST = 1

DEFAULT_BURST_CAPACITY = 100


# Priority Levels

CRITICAL_PRIORITY = 0

HIGH_PRIORITY = 1

NORMAL_PRIORITY = 2


# Queue Defaults

DEFAULT_AGING_THRESHOLD_SECONDS = 5


# Benchmark Settings

DEFAULT_BURST_REQUESTS = 10_000


# Redis Simulation

DEFAULT_REDIS_LATENCY_MS = 50
