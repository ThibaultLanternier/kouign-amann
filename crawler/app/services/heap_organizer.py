from abc import ABC, abstractmethod
from datetime import timedelta
import logging

from app.entities.picture_data import iPictureData
from app.entities.picture_heap import HeapType, PictureHeap, iPictureHeap


class iHeapOrganizer(ABC):
    @abstractmethod
    def reorganize_heaps(self, event_list: list[iPictureHeap]) -> list[iPictureHeap]:
        pass


class TimeDifferenceHeapOrganizer(iHeapOrganizer):
    def __init__(self, max_time_difference: timedelta, min_heap_size: int) -> None:
        self._max_time_difference = max_time_difference
        self._min_heap_size = min_heap_size

        self._logger = logging.getLogger("app.time_difference_heap_organizer")

    def _describe_heap(self, heap: iPictureHeap) -> str:
        description = heap.get_description() if heap.get_description() else "NONE"
        heap_date = heap.get_start_date().date()
        picture_count = len(heap.get_picture_list())

        return f"{heap_date} - {description} - {picture_count} pictures"

    def _most_common_description(
        self, picture_and_heap_list: list[tuple[iPictureData, iPictureHeap]]
    ) -> str | None:
        description_count: dict[str, int] = {}

        for picture_and_heap in picture_and_heap_list:
            heap = picture_and_heap[1]

            description = heap.get_description()
            if description is not None:
                if description in description_count:
                    description_count[description] += 1
                else:
                    description_count[description] = 1

        most_common_description = None
        highest_count = 0

        for description, count in description_count.items():
            if count > highest_count:
                highest_count = count
                most_common_description = description

        return most_common_description

    def _get_ordered_pictures(
        self, heap_list: list[iPictureHeap]
    ) -> list[tuple[iPictureData, iPictureHeap]]:
        picture_and_heap_list: list[tuple[iPictureData, iPictureHeap]] = []

        for heap in heap_list:
            picture_and_heap_list.extend(
                (picture, heap) for picture in heap.get_picture_list()
            )

        return sorted(
            picture_and_heap_list,
            key=lambda picture: picture[0].get_creation_date(),
        )

    def _create_picture_heap(
        self, picture_and_heap_list: list[tuple[iPictureData, iPictureHeap]]
    ) -> iPictureHeap:
        description = self._most_common_description(picture_and_heap_list)

        picture_list = [
            picture_and_heap[0] for picture_and_heap in picture_and_heap_list
        ]

        heap = PictureHeap(
            heap_type=HeapType.GROUPED,
            picture_list=picture_list,
            description=description,
        )
        self._logger.debug(f"Adding heap {self._describe_heap(heap=heap)}")

        return heap

    def _regroup_too_small_heaps(
        self, heap_list: list[iPictureHeap]
    ) -> list[iPictureHeap]:
        output: list[iPictureHeap] = []
        other_pictures: list[iPictureData] = []

        for heap in heap_list:
            if len(heap.get_picture_list()) < self._min_heap_size:
                self._logger.debug(
                    f"Moving heap to other - {self._describe_heap(heap=heap)}"
                )
                other_pictures.extend(heap.get_picture_list())
            else:
                output.append(heap)

        other_heap = PictureHeap(
            heap_type=HeapType.OTHER, picture_list=other_pictures, description=None
        )

        output.append(other_heap)

        return output

    def reorganize_heaps(self, event_list: list[iPictureHeap]) -> list[iPictureHeap]:
        ordered_picture_and_heap_list: list[tuple[iPictureData, iPictureHeap]] = (
            self._get_ordered_pictures(event_list)
        )

        output: list[iPictureHeap] = []
        current_group: list[tuple[iPictureData, iPictureHeap]] = []

        previous_picture: iPictureData | None = None

        for picture_and_heap in ordered_picture_and_heap_list:
            picture = picture_and_heap[0]

            if previous_picture is None:
                current_group.append(picture_and_heap)
            else:
                time_difference = (
                    picture.get_creation_date() - previous_picture.get_creation_date()
                )

                if (
                    time_difference <= self._max_time_difference
                    and not picture.is_group_break()
                ):
                    current_group.append(picture_and_heap)
                else:
                    if picture.is_group_break():
                        self._logger.debug(
                            f"Breaking group : forced at picture {picture.get_hash()}"
                        )
                    else:
                        self._logger.debug(
                            f"Breaking group time difference: {time_difference}"
                        )

                    output.append(self._create_picture_heap(current_group))
                    current_group = [picture_and_heap]

            previous_picture = picture

        output.append(self._create_picture_heap(current_group))

        return self._regroup_too_small_heaps(output)
