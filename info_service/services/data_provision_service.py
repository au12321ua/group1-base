"""DataProvisionService — serve master data snapshots to B/C/F systems."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession


class DataProvisionService:
    """Provides teacher lists, calendars, training programs, etc. to B/C/F systems.

    All responses include snapshotTime or version fields.
    Uses Service Token authentication (validated by Gateway).
    """

    def __init__(self) -> None:
        warnings.warn("TODO: DataProvisionService — implement all methods")

    async def list_teachers(self, db: AsyncSession, page: int = 1, page_size: int = 100) -> tuple[list, int]:
        """List all teachers (role=TEACHER) for B system consumption."""
        warnings.warn("TODO: implement list_teachers")
        raise NotImplementedError("list_teachers not implemented")

    async def list_candidate_students(
        self, db: AsyncSession, page: int = 1, page_size: int = 100
    ) -> tuple[list, int]:
        """List candidate students for B system."""
        warnings.warn("TODO: implement list_candidate_students")
        raise NotImplementedError("list_candidate_students not implemented")

    async def get_calendars(self, db: AsyncSession) -> list:
        """Get all academic calendars for B system."""
        warnings.warn("TODO: implement get_calendars")
        raise NotImplementedError("get_calendars not implemented")

    async def list_training_programs(
        self, db: AsyncSession, page: int = 1, page_size: int = 100
    ) -> tuple[list, int]:
        """List training programs for C system."""
        warnings.warn("TODO: implement list_training_programs")
        raise NotImplementedError("list_training_programs not implemented")

    async def query_selected_students(
        self, db: AsyncSession, **filters
    ) -> dict:
        """Proxy to C system for selected students query. Not stored locally."""
        warnings.warn("TODO: implement query_selected_students — proxy to C system")
        raise NotImplementedError("query_selected_students not implemented")


data_provision_service = DataProvisionService()
