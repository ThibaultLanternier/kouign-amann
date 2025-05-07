from zipp import Path

from app.use_cases.backup import baseUseCase
from crawler.app.services.group_creator import iGroupCreatorService


class GroupUseCase(baseUseCase):
    def __init__(self, group_creator_service: iGroupCreatorService):
        self._group_creator_service = group_creator_service

    def group(self, picture_list: list[Path]):
        raise NotImplementedError("GroupUseCase.group() is not implemented")
