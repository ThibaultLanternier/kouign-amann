from abc import ABC, abstractmethod, abstractproperty
import re

from pathlib import Path
from datetime import date, datetime

class PicturePathException(Exception):
    pass

class FileNotFoundException(PicturePathException):
    pass

class MalformedFileNameException(PicturePathException):
    pass

class abstractPicturePath(ABC):
    @abstractmethod
    def get_day(self) -> date:
        pass

    @abstractmethod
    def get_folder_path(self) -> Path:
        pass

    @abstractmethod
    def get_hash(self) -> str:
        pass
    
    @abstractmethod
    def get_year(self) -> int:
        pass

class PicturePath(abstractPicturePath):
    __day: date
    __year: int
    __folder_path: Path
    __hash: str

    def __extract_infos(self, file_name: str) -> tuple[int, str]:
        pattern = re.compile(r'^([0-9]{10})-([a-f0-9]+).jpg$')
        m = re.match(pattern, file_name)
        
        if m is None:
            raise MalformedFileNameException(f'File name {file_name} is malformed')

        return int(m.group(1)), m.group(2)


    def __init__(self, path: Path):
        self.__path = path

        if not self.__path.is_file():
            raise FileNotFoundException(f'Path {self.__path} is not a file')
        
        self.__timestamp, self.__hash = self.__extract_infos(self.__path.name)

        self.__date_time = datetime.fromtimestamp(self.__timestamp)
        
        self.__year = self.__date_time.year
        self.__day = self.__date_time.date()
        self.__folder_path = self.__path.parent
    
    def get_day(self) -> date:
        return self.__day
    
    def get_folder_path(self) -> Path: 
        return self.__folder_path
    
    def get_hash(self) -> str:
        return self.__hash
    
    def get_year(self) -> int:
        return self.__year

