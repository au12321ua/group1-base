"""TrainingProgram CRUD — curriculum plan operations."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.training_program import TrainingProgram


class TrainingProgramCRUD(BaseCRUD[TrainingProgram]):
    """Data access for TrainingProgram model."""

    def __init__(self) -> None:
        super().__init__(TrainingProgram)
        warnings.warn("TODO: TrainingProgramCRUD — implement custom query methods")

    async def get_by_program_code(self, db: AsyncSession, code: str) -> TrainingProgram | None:
        """Get program by program_code."""
        warnings.warn("TODO: implement get_by_program_code")
        raise NotImplementedError("get_by_program_code not implemented")

    async def get_by_major(
        self, db: AsyncSession, major_code: str, grade: str | None = None
    ) -> list[TrainingProgram]:
        """Get programs by major code, optionally filtered by grade."""
        warnings.warn("TODO: implement get_by_major")
        raise NotImplementedError("get_by_major not implemented")


training_program_crud = TrainingProgramCRUD()
