import os
import sys
import asyncio
import time

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )

from algorithms.sliding_window import (
    SlidingWindowCounter
)

from storage.redis_simulator import (
    RedisSimulator
)


TOTAL_REQUESTS = 10_000
REQUEST_LIMIT = 100
WINDOW_SIZE_SECONDS = 1
BATCH_SIZE = 500


async def execute_request_batch(
    limiter: SlidingWindowCounter,
    batch_size: int
):

    tasks = [

        limiter.is_allowed(
            client_id="burst_client"
        )

        for _ in range(
            batch_size
        )
    ]

    return await asyncio.gather(
        *tasks
    )


async def run_burst_benchmark():

    redis_client = RedisSimulator(
        latency_ms=0
    )

    limiter = SlidingWindowCounter(

        redis_client=redis_client,

        request_limit=REQUEST_LIMIT,

        window_size_seconds=WINDOW_SIZE_SECONDS
    )

    benchmark_start = (
        time.perf_counter()
    )

    all_responses = []

    for batch_start in range(

        0,

        TOTAL_REQUESTS,

        BATCH_SIZE
    ):

        batch_results = await execute_request_batch(

            limiter,

            BATCH_SIZE
        )

        all_responses.extend(
            batch_results
        )

    benchmark_duration = (

        time.perf_counter()

        - benchmark_start
    )

    allowed_requests = sum(

        response["allowed"]

        for response in all_responses
    )

    blocked_requests = (

        len(all_responses)

        - allowed_requests
    )

    throughput = (

        len(all_responses)

        / benchmark_duration
    )

    print("\n========== Burst Traffic Benchmark ==========")

    print(
        f"Total Requests      : {TOTAL_REQUESTS}"
    )

    print(
        f"Allowed Requests    : {allowed_requests}"
    )

    print(
        f"Blocked Requests    : {blocked_requests}"
    )

    print(
        f"Execution Time      : {benchmark_duration:.2f}s"
    )

    print(
        f"Throughput          : {throughput:.2f} req/sec"
    )

    print("=============================================")


if __name__ == "__main__":

    asyncio.run(
        run_burst_benchmark()
    )
