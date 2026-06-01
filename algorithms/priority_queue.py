import time

from dataclasses import dataclass
from threading import Lock
from typing import Any, Callable, List, Optional

from config.constants import (
    CRITICAL_PRIORITY,
    HIGH_PRIORITY,
    NORMAL_PRIORITY,
    DEFAULT_AGING_THRESHOLD_SECONDS
)


@dataclass(slots=True)
class QueueItem:
    

    request_id: str

    payload: Any

    priority: int

    created_timestamp: float

    insertion_order: int

    age_boost_applied: bool = False


class PriorityScheduler:

    def __init__(
        self,
        aging_threshold_seconds: int = (
            DEFAULT_AGING_THRESHOLD_SECONDS
        ),
        clock: Callable[
            [],
            float
        ] = time.time
    ):

        if aging_threshold_seconds <= 0:

            raise ValueError(
                "aging threshold must be positive"
            )

        self.clock = clock

        self.aging_threshold_seconds = (
            aging_threshold_seconds
        )

        self.heap: List[
            QueueItem
        ] = []

        self.sequence_counter = 0

        self._lock = Lock()

    def insert(
        self,
        request_id: str,
        payload: Any,
        priority: int
    ):

        normalized_request_id = (
            request_id.strip()
        )

        if not normalized_request_id:

            raise ValueError(
                "request_id cannot be empty"
            )

        if priority not in {

            CRITICAL_PRIORITY,

            HIGH_PRIORITY,

            NORMAL_PRIORITY
        }:

            raise ValueError(
                "invalid priority"
            )

        with self._lock:

            queue_item = QueueItem(

                request_id=(
                    normalized_request_id
                ),

                payload=payload,

                priority=priority,

                created_timestamp=(
                    self.clock()
                ),

                insertion_order=(
                    self.sequence_counter
                )
            )

            self.sequence_counter += 1

            self.heap.append(
                queue_item
            )

            self._heapify_up(
                len(self.heap) - 1
            )

    def extract_next(
        self
    ):

        with self._lock:

            if not self.heap:

                return None

            self._apply_priority_aging()

            selected_item = (
                self.heap[0]
            )

            last_item = (
                self.heap.pop()
            )

            if self.heap:

                self.heap[0] = (
                    last_item
                )

                self._heapify_down(
                    0
                )

            return selected_item

    def _apply_priority_aging(
        self
    ):

        current_time = (
            self.clock()
        )

        heap_changed = False

        for item in self.heap:

            waiting_time = (

                current_time -

                item.created_timestamp
            )

            should_promote = (

                waiting_time >=

                self.aging_threshold_seconds

                and

                not item.age_boost_applied

                and

                item.priority >

                CRITICAL_PRIORITY
            )

            if should_promote:

                item.priority -= 1

                item.age_boost_applied = True

                heap_changed = True

        if heap_changed:

            for index in reversed(

                range(
                    len(self.heap) // 2
                )
            ):

                self._heapify_down(
                    index
                )

    def _has_higher_priority(
        self,
        left: QueueItem,
        right: QueueItem
    ):

        if left.priority != right.priority:

            return (

                left.priority <

                right.priority
            )

        return (

            left.insertion_order <

            right.insertion_order
        )

    def _heapify_up(
        self,
        index: int
    ):

        while index > 0:

            parent_index = (
                index - 1
            ) // 2

            if not self._has_higher_priority(

                self.heap[index],

                self.heap[parent_index]
            ):

                break

            self.heap[index], self.heap[parent_index] = (

                self.heap[parent_index],

                self.heap[index]
            )

            index = parent_index

    def _heapify_down(
        self,
        index: int
    ):

        heap_size = len(
            self.heap
        )

        while True:

            smallest = index

            left_child = (
                index * 2
            ) + 1

            right_child = (
                index * 2
            ) + 2

            if (

                left_child < heap_size

                and

                self._has_higher_priority(

                    self.heap[left_child],

                    self.heap[smallest]
                )
            ):

                smallest = left_child

            if (

                right_child < heap_size

                and

                self._has_higher_priority(

                    self.heap[right_child],

                    self.heap[smallest]
                )
            ):

                smallest = right_child

            if smallest == index:

                return

            self.heap[index], self.heap[smallest] = (

                self.heap[smallest],

                self.heap[index]
            )

            index = smallest
