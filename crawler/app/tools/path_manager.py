from app.tools.path import abstractPicturePath
from datetime import date
from pathlib import Path


class PicturePathManager:
    _by_day: dict[date, Path]
    _by_hash: dict[str, abstractPicturePath]
    _root_folder: Path

    def __init__(self, picture_path_list: list[abstractPicturePath], root_folder: Path):
        self._by_day = {}
        self._by_hash = {}
        self._root_folder = root_folder

        [self.add_picture_path(x) for x in picture_path_list]

    def _regroup_adjacent_days(self):
        day_list = sorted(self._by_day.keys())

        for index in range(1, len(day_list)):
            previous_day = day_list[index - 1]
            current_day = day_list[index]

            time_difference = current_day - previous_day

            if time_difference.days <= 1:
                self._by_day[current_day] = self._by_day[previous_day]

    def _add_new_path_if_not_exists(self, picture_path: abstractPicturePath):
        day_list = sorted(self._by_day.keys())

        for day in day_list:
            time_difference = picture_path.get_day() - day
            if abs(time_difference.days) <= 1:
                self._by_day[picture_path.get_day()] = self._by_day[day]
                return

        self._by_day[picture_path.get_day()] = picture_path.get_folder_path()

    def add_picture_path(self, picture_path: abstractPicturePath):
        if not isinstance(picture_path, abstractPicturePath):
            raise Exception("invalid PicturePath object")

        self._by_hash[picture_path.get_hash()] = picture_path
        self._add_new_path_if_not_exists(picture_path)

        self._regroup_adjacent_days()

    def get_folder_path(self, picture_day: date, group_event: bool = True) -> Path:
        if group_event:
            day_list = sorted(self._by_day.keys())

            for day in day_list:
                time_difference = picture_day - day
                if abs(time_difference.days) <= 1:
                    return self._by_day[day]

            return (
                self._root_folder
                / Path(f"{picture_day.year}")
                / Path(f"{picture_day} <EVENT_DESCRIPTION>")
            )
        else:
            return self._root_folder / Path(f"{picture_day.year}") / Path("NOT_GROUPED")

    def check_hash_exists(self, hash: str) -> bool:
        return hash in self._by_hash
