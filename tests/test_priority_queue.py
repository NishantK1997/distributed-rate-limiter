from algorithms.priority_queue import (
    PriorityScheduler,
    CRITICAL_PRIORITY,
    HIGH_PRIORITY,
    NORMAL_PRIORITY
)


def test_should_process_high_priority_first():

    scheduler = PriorityScheduler()

    scheduler.insert(
        "normal_request",
        {},
        NORMAL_PRIORITY
    )

    scheduler.insert(
        "critical_request",
        {},
        CRITICAL_PRIORITY
    )

    next_item = (
        scheduler.extract_next()
    )

    assert (
        next_item.request_id
        ==
        "critical_request"
    )


def test_should_preserve_fifo_order():

    scheduler = PriorityScheduler()

    scheduler.insert(
        "request_1",
        {},
        HIGH_PRIORITY
    )

    scheduler.insert(
        "request_2",
        {},
        HIGH_PRIORITY
    )

    first = scheduler.extract_next()

    second = scheduler.extract_next()

    assert first.request_id == "request_1"

    assert second.request_id == "request_2"


def test_should_return_none_for_empty_queue():

    scheduler = PriorityScheduler()

    assert (

        scheduler.extract_next()

        is None
    )


def test_should_validate_priority():

    scheduler = PriorityScheduler()

    try:

        scheduler.insert(
            "request",
            {},
            100
        )

        assert False

    except ValueError:

        assert True


def test_should_apply_priority_aging():

    fake_time = [100]

    def mock_clock():

        return fake_time[0]

    scheduler = PriorityScheduler(

        aging_threshold_seconds=5,

        clock=mock_clock
    )

    scheduler.insert(
        "normal_job",
        {},
        NORMAL_PRIORITY
    )

    fake_time[0] += 6

    item = scheduler.extract_next()

    assert item.priority < NORMAL_PRIORITY
