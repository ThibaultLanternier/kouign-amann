from math import pi
from pathlib import Path
import re
from turtle import pd
from app.tools.path import abstractPicturePath

class PictureGroup:
    def __init__(self, picture_path_list: list[abstractPicturePath]):
        if len(picture_path_list) == 0:
            raise Exception("A group must contain at least one picture path")

        self._picture_path_list = picture_path_list
        self._picture_path_count = {}

        for picture_path in self._picture_path_list:
            folder_path = picture_path.get_folder_path()
            folder_name = folder_path.name

            if folder_name != 'NOT_GROUPED':
                if folder_path not in self._picture_path_count:
                    self._picture_path_count[folder_path] = 0
                
                self._picture_path_count[folder_path] = self._picture_path_count[folder_path] + 1
            
        
        def picture_count(item) -> int:
            return item[1]

        self._folder_list = [k for (k,v) in sorted(self._picture_path_count.items(),key=picture_count, reverse=True)]

        if(len(self._folder_list) == 0):
            root_folder = picture_path_list[0].get_folder_path().parent
            self._folder_list = [ root_folder / Path(f"{picture_path_list[0].get_day()} <EVENT_DESCRIPTION>") ]
        
    def get_folder_path(self) -> Path:
        return self._folder_list[0]
    
    def list_pictures_to_move(self) -> tuple[Path, Path]:
        output = []
        
        for picture in self._picture_path_list:
            if(self.get_folder_path() != picture.get_folder_path()):
                origin_path = picture.get_path()
                target_path = self.get_folder_path() / picture.get_path().name

                output.append((origin_path, target_path))
        
        return output

class PictureGrouper:
    def __init__(self, picture_path_list: list[abstractPicturePath]):
        self._picture_path_list = picture_path_list

    def group_pictures(self, max_days: int = 1 ) -> list[list[abstractPicturePath]]:
        sorted_picture_path_list = sorted(self._picture_path_list, key=lambda x: x.get_day())
        grouped_picture_path = []
        current_group = []
        
        previous_picture = None

        for picture_path in sorted_picture_path_list:
            if previous_picture == None:
                current_group.append(picture_path)
            else:
                time_difference = picture_path.get_day() - previous_picture.get_day()

                if time_difference.days <= max_days:
                    current_group.append(picture_path)
                else:
                    grouped_picture_path.append(current_group)
                    current_group = [picture_path]
            
            previous_picture = picture_path
        
        grouped_picture_path.append(current_group)

        return grouped_picture_path
            