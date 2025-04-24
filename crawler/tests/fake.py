from datetime import date
from pathlib import Path
from app.tools.path import abstractPicturePath


class FakePicturePath(abstractPicturePath):
    def __init__(self, folder_path: Path, day: date, hash: str):
        self.__folder_path = folder_path
        self.__day = day
        self.__hash = hash

    def get_day(self) -> date:
        return self.__day

    def get_folder_path(self) -> Path:
        return self.__folder_path

    def get_hash(self) -> str:
        return self.__hash

    def get_year(self) -> int:
        return self.__day.year
    
    def __repr__(self) -> str:
        return self.__hash