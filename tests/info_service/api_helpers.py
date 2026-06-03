"""Info Service 集成测试的通用辅助函数。"""

from httpx import AsyncClient, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.main import info_engine
from info_service.models.classroom import Classroom
from tests.utils import build_identity_headers, make_course_payload


def _default_auth_headers(resource: str) -> dict[str, str]:
    """Build auth headers with standard CRUD permissions for a resource."""
    return build_identity_headers(
        permissions=[f"{resource}:{action}" for action in ("read", "create", "update", "delete")]
    )


def assert_status_and_data(response: Response, expected_status: int = 200) -> dict:
    """断言 HTTP 状态码并返回 APIResponse.data。"""
    assert response.status_code == expected_status
    return response.json()["data"]


async def create_course(
    async_client_info: AsyncClient,
    *,
    course_code: str,
    course_name: str,
    credit: int = 3,
    capacity: int = 80,
    auth_headers: dict[str, str] | None = None,
) -> int:
    """创建课程并返回 course_id。"""
    if auth_headers is None:
        auth_headers = _default_auth_headers("course")
    response = await async_client_info.post(
        "/api/v1/info/courses/",
        json=make_course_payload(
            course_code=course_code,
            course_name=course_name,
            credit=credit,
            capacity=capacity,
        ),
        headers=auth_headers,
    )
    return assert_status_and_data(response)["id"]


async def create_offering(
    async_client_info: AsyncClient,
    *,
    course_id: int,
    term_code: str,
    class_no: str,
    capacity: int = 60,
    auth_headers: dict[str, str] | None = None,
) -> int:
    """创建开课记录并返回 offering_id。"""
    if auth_headers is None:
        auth_headers = _default_auth_headers("offering")
    response = await async_client_info.post(
        "/api/v1/info/offerings/",
        json={
            "course_id": course_id,
            "term_code": term_code,
            "class_no": class_no,
            "capacity": capacity,
        },
        headers=auth_headers,
    )
    return assert_status_and_data(response)["id"]


async def create_schedule(
    async_client_info: AsyncClient,
    *,
    offering_id: int,
    classroom_id: int,
    day_of_week: int,
    start_period: int,
    end_period: int,
    week_range: str = "1-16",
    auth_headers: dict[str, str] | None = None,
) -> int:
    """创建排课记录并返回 schedule_id。"""
    if auth_headers is None:
        auth_headers = _default_auth_headers("schedule")
    response = await async_client_info.post(
        "/api/v1/info/schedules/",
        json={
            "offering_id": offering_id,
            "classroom_id": classroom_id,
            "day_of_week": day_of_week,
            "start_period": start_period,
            "end_period": end_period,
            "week_range": week_range,
        },
        headers=auth_headers,
    )
    return assert_status_and_data(response)["id"]


async def create_classroom(
    *,
    room_no: str,
    building: str = "Main",
    capacity: int = 80,
) -> int:
    """直接写入测试数据库创建教室并返回 classroom_id。"""
    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        classroom = Classroom(
            room_no=room_no,
            building=building,
            capacity=capacity,
        )
        session.add(classroom)
        await session.commit()
        await session.refresh(classroom)
        return classroom.id
