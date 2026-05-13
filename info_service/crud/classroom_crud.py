"""Classroom CRUD — classroom resource operations."""

import warnings

from info_service.crud.base import BaseCRUD
from info_service.models.classroom import Classroom


class ClassroomCRUD(BaseCRUD[Classroom]):
    """Data access for Classroom model."""

    def __init__(self) -> None:
        super().__init__(Classroom)
        warnings.warn("TODO: ClassroomCRUD — implement custom query methods")


classroom_crud = ClassroomCRUD()
