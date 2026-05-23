"""Classroom model — physical teaching space."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Classroom(SQLModel, table=True):
    """Classroom/teaching space resource."""

    __tablename__: str = "classrooms"

    id: int | None = Field(default=None, primary_key=True)
    room_no: str = Field(max_length=64, unique=True)
    building: str = Field(default="", max_length=128)
    capacity: int = Field(default=0)
    type: str = Field(default="standard", max_length=64)  # standard / lab / lecture_hall
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
