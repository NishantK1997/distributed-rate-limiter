from algorithms.priority_queue import (
    PriorityScheduler,
    HIGH_PRIORITY,
    NORMAL_PRIORITY
)


def test_should_prioritize_high_priority_requests():

    scheduler = PriorityScheduler()

    for request_number in range(100):

        scheduler.insert(

            request_id=f"low_{request_number}",

            payload={},

            priority=NORMAL_PRIORITY
        )

    for request_number in range(10):

        scheduler.insert(

            request_id=f"high_{request_number}",

            payload={},

            priority=HIGH_PRIORITY
        )

    processed_requests = []

    for _ in range(10):

        request = scheduler.extract_next()

        processed_requests.append(
            request.request_id
        )

    assert all(

        request.startswith(
            "high_"
        )

        for request in processed_requests
    )
