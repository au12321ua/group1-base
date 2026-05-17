"""DataProvision schemas — responses for B/C/F system consumption."""

from datetime import datetime

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


class DataProvisionWrapper(BaseModel):
    """Wrapper for data provision responses with snapshot metadata."""
    items: list
    pagination: dict
    snapshot_time: datetime
    version: str = "1.0"


class SelectedStudentsResponse(BaseModel):
    """Proxy response from C (选课) system — passed through by Info Service."""
    items: list
    pagination: dict
