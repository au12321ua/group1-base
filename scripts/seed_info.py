"""Seed Info DB with admin UserInfo/UserProfile and optional sample data."""

from datetime import UTC, datetime

from sqlalchemy.engine import Engine
from sqlmodel import Session

from scripts.seed_utils import is_table_empty, print_step

# ── Admin user info ────────────────────────────────────────────────────────────

def seed_admin_user_info(
    engine: Engine,
    username: str = "admin",
    user_no: str = "STSS-ADMIN-001",
    full_name: str = "系统管理员",
) -> int:
    """Create UserInfo + UserProfile for the admin user. Returns user_info id."""
    from info_service.models.user import UserInfo
    from info_service.models.user_profile import UserProfile

    if not is_table_empty(engine, "users_info"):
        print_step("users_info 表非空，跳过")
        with Session(engine) as session:
            user = session.query(UserInfo).filter(UserInfo.username == username).first()
            if user:
                return user.id
            return 0

    with Session(engine) as session:
        now = datetime.now(UTC)
        user_info = UserInfo(
            user_no=user_no,
            username=username,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )
        session.add(user_info)
        session.flush()

        profile = UserProfile(
            user_id=user_info.id,
            full_name=full_name,
            gender="",
            email=f"{username}@stss.local",
            phone="",
            status="ACTIVE",
            created_at=now,
            updated_at=now,
        )
        session.add(profile)
        session.commit()

        user_info_id = user_info.id
    print_step(f"已创建管理员 Info 记录: username={username}, id={user_info_id}")
    return user_info_id


# ── Full-mode sample data ──────────────────────────────────────────────────────

_SAMPLE_BASE_INFO: list[dict] = [
    # 院系
    {"category": "department", "item_code": "CS", "item_name": "计算机学院"},
    {"category": "department", "item_code": "MATH", "item_name": "数学学院"},
    {"category": "department", "item_code": "PHYS", "item_name": "物理学院"},
    {"category": "department", "item_code": "CHEM", "item_name": "化学学院"},
    {"category": "department", "item_code": "BIO", "item_name": "生命科学学院"},
    {"category": "department", "item_code": "ENG", "item_name": "工程学院"},
    # 职称
    {"category": "title", "item_code": "PROF", "item_name": "教授"},
    {"category": "title", "item_code": "ASSO_PROF", "item_name": "副教授"},
    {"category": "title", "item_code": "LECT", "item_name": "讲师"},
    {"category": "title", "item_code": "ASSIST", "item_name": "助教"},
    # 考核方式
    {"category": "assessment_method", "item_code": "EXAM", "item_name": "考试"},
    {"category": "assessment_method", "item_code": "CHECK", "item_name": "考查"},
    {"category": "assessment_method", "item_code": "PAPER", "item_name": "论文"},
    # 学期
    {"category": "term_type", "item_code": "FALL", "item_name": "秋季学期"},
    {"category": "term_type", "item_code": "SPRING", "item_name": "春季学期"},
]


def seed_base_info_items(engine: Engine) -> None:
    """Insert sample BaseInfoItem records (departments, titles, etc.)."""
    from info_service.models.base_info_item import BaseInfoItem

    if not is_table_empty(engine, "base_info_items"):
        print_step("base_info_items 表非空，跳过")
        return

    with Session(engine) as session:
        now = datetime.now(UTC)
        for item in _SAMPLE_BASE_INFO:
            session.add(
                BaseInfoItem(
                    category=item["category"],
                    item_code=item["item_code"],
                    item_name=item["item_name"],
                    description="",
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
            )
        session.commit()
    print_step(f"已创建 {len(_SAMPLE_BASE_INFO)} 条基础数据")


_SAMPLE_CLASSROOMS: list[dict] = [
    {"room_no": "博学楼101", "building": "博学楼", "capacity": 200, "type": "standard"},
    {"room_no": "博学楼201", "building": "博学楼", "capacity": 150, "type": "standard"},
    {"room_no": "博学楼301", "building": "博学楼", "capacity": 120, "type": "standard"},
    {"room_no": "致远楼102", "building": "致远楼", "capacity": 100, "type": "standard"},
    {"room_no": "致远楼202", "building": "致远楼", "capacity": 80, "type": "standard"},
    {"room_no": "实验室A301", "building": "实验楼A", "capacity": 60, "type": "lab"},
    {"room_no": "实验室A302", "building": "实验楼A", "capacity": 60, "type": "lab"},
    {"room_no": "实验室B101", "building": "实验楼B", "capacity": 40, "type": "lab"},
    {"room_no": "学术报告厅", "building": "行政楼", "capacity": 500, "type": "lecture_hall"},
    {"room_no": "阶梯教室101", "building": "教学楼C", "capacity": 300, "type": "lecture_hall"},
]


def seed_classrooms(engine: Engine) -> None:
    """Insert sample Classroom records."""
    from info_service.models.classroom import Classroom

    if not is_table_empty(engine, "classrooms"):
        print_step("classrooms 表非空，跳过")
        return

    with Session(engine) as session:
        now = datetime.now(UTC)
        for room in _SAMPLE_CLASSROOMS:
            session.add(
                Classroom(
                    room_no=room["room_no"],
                    building=room["building"],
                    capacity=room["capacity"],
                    type=room["type"],
                    created_at=now,
                    updated_at=now,
                )
            )
        session.commit()
    print_step(f"已创建 {len(_SAMPLE_CLASSROOMS)} 间教室")


def seed_academic_calendars(engine: Engine) -> None:
    """Insert sample AcademicCalendar records."""
    from datetime import date

    from info_service.models.academic_calendar import AcademicCalendar

    if not is_table_empty(engine, "academic_calendars"):
        print_step("academic_calendars 表非空，跳过")
        return

    terms = [
        {
            "term_code": "2025-2026-1",
            "term_name": "2025-2026 学年第一学期",
            "start_date": date(2025, 9, 1),
            "end_date": date(2026, 1, 16),
        },
        {
            "term_code": "2025-2026-2",
            "term_name": "2025-2026 学年第二学期",
            "start_date": date(2026, 2, 23),
            "end_date": date(2026, 7, 3),
        },
    ]

    with Session(engine) as session:
        now = datetime.now(UTC)
        for t in terms:
            session.add(
                AcademicCalendar(
                    term_code=t["term_code"],
                    term_name=t["term_name"],
                    start_date=t["start_date"],
                    end_date=t["end_date"],
                    version="1.0",
                    snapshot_time=now,
                    created_at=now,
                    updated_at=now,
                )
            )
        session.commit()
    print_step(f"已创建 {len(terms)} 条校历")
