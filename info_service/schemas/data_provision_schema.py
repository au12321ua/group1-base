"""DataProvision schemas — responses for B/C/F system consumption."""

from datetime import date, datetime

from pydantic import BaseModel


class TeacherDataResponse(BaseModel):
    """Teacher info provided to B (排课) system."""
    user_id: str
    user_no: str
    username: str
    full_name: str
    email: str = ""
    phone: str = ""


class CandidateStudentResponse(BaseModel):
    """Candidate student info provided to B system."""
    user_id: str
    user_no: str
    username: str
    full_name: str
    grade: str = ""


class AcademicCalendarDataResponse(BaseModel):
    """Academic calendar snapshot provided to B system."""

    id: int
    term_code: str
    term_name: str
    start_date: date
    end_date: date
    version: str = "1.0"
    snapshot_time: datetime


class TrainingProgramDataResponse(BaseModel):
    """Training program snapshot provided to C system."""

    id: int
    program_code: str
    major_code: str
    grade: str
    version: str = "1.0"
    required_course_ids: list[int]
    snapshot_time: datetime


class DataProvisionWrapper(BaseModel):
    """Wrapper for data provision responses with snapshot metadata."""
    items: list
    pagination: dict
    snapshot_time: datetime
    version: str = "1.0"


class SelectedStudentsResponse(BaseModel):
    """Normalized selected student response from C system."""

    items: list
    pagination: dict
    snapshot_time: datetime
    version: str = "1.0"
