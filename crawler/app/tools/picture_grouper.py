from turtle import pd
from app.tools.path import abstractPicturePath


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
            