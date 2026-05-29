import time

from dataclasses import dataclass
from threading import Lock
from typing import Any, Callable, List, Optional


CRITICAL_PRIORITY = 0
HIGH_PRIORITY = 1
NORMAL_PRIORITY = 2

DEFAULT_AGING_THRESHOLD_SECONDS = 5


@dataclass(slots=True)
class QueueItem:

    request_id: str

    payload: Any

    priority: int

    created_timestamp: float

    insertion_order: int

    has_received_age_boost: bool = False


class PriorityScheduler:

    def __init__(
        self,
        aging_threshold_seconds: int = (
            DEFAULT_AGING_THRESHOLD_SECONDS
        ),
        clock: Callable[[], float] = time.time
    ) -> None:

        if aging_threshold_seconds <= 0:

            raise ValueError(
                "aging_threshold_seconds must be positive"
            )

        self.clock = clock

        self.aging_threshold_seconds = (
            aging_threshold_seconds
        )

        self.heap: List[
            QueueItem
        ] = []

        self.sequence_counter = 0

        self.lock = Lock()

    def insert(
        self,
        request_id: str,
        payload: Any,
        priority: int
    ) -> None:

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
                "invalid priority value"
            )

        with self.lock:

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
    ) -> Optional[QueueItem]:

        with self.lock:

            if not self.heap:

                return None

            self._apply_priority_aging()

            highest_priority_item = (
                self.heap[0]
            )

            last_item = (
                self.heap.pop()
            )

            if self.heap:

                self.heap[0] = last_item

                self._heapify_down(0)

            return highest_priority_item

    def _apply_priority_aging(
        self
    ) -> None:

        current_time = self.clock()

        heap_updated = False

        for item in self.heap:

            waiting_time = (

                current_time -

                item.created_timestamp
            )

            should_promote = (

                waiting_time >=
                self.aging_threshold_seconds

                and

                not item.has_received_age_boost

                and

                item.priority >
                CRITICAL_PRIORITY
            )

            if should_promote:

                item.priority -= 1

                item.has_received_age_boost = True

                heap_updated = True

        if heap_updated:

            for index in reversed(

                range(
                    len(self.heap) // 2
                )
            ):

                self._heapify_down(
                    index
                )

    def _is_higher_priority(
        self,
        left: QueueItem,
        right: QueueItem
    ) -> bool:

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
    ) -> None:

        while index > 0:

            parent_index = (
                index - 1
            ) // 2

            if not self._is_higher_priority(

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
    ) -> None:

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

                self._is_higher_priority(

                    self.heap[left_child],

                    self.heap[smallest]
                )
            ):

                smallest = left_child

            if (

                right_child < heap_size

                and

                self._is_higher_priority(

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
        