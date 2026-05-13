"""TrainingProgram model — degree/major curriculum plan."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TrainingProgram(SQLModel, table=True):
    """Training program / curriculum plan for a major."""

    __tablename__ = "training_programs"

    id: Optional[int] = Field(default=None, primary_key=True)
    program_code: str = Field(max_length=64, unique=True, index=True)
    major_code: str = Field(max_length=64, index=True)
    grade: str = Field(max_length=16)  # e.g. "2024"
    version: str = Field(default="1.0", max_length=16)
    required_course_ids: str = Field(default="", max_length=1024)  # comma-separated
    snapshot_time: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
