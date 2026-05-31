"""开课 API 集成测试。"""

import pytest

from tests.info_service.api_helpers import (
    assert_status_and_data,
    create_course,
    create_offering,
)


@pytest.mark.integration
class TestOfferingAPI:
    """验证 /api/v1/offerings 的 CRUD 及关键约束。"""

    async def test_offering_crud_flow(self, async_client_info, auth_headers) -> None:
        """应支持创建、查询、列表、更新和删除开课记录。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS510",
            course_name="Distributed Systems",
            capacity=120,
        )

        create_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "teacher_ids": ["t-1", "t-2"],
                "capacity": 80,
            },
            headers=auth_headers,
        )

        created = assert_status_and_data(create_resp)
        assert created["course_id"] == course_id
        assert created["teacher_ids"] == "t-1,t-2"
        offering_id = created["id"]

        list_resp = await async_client_info.get(
            "/api/v1/offerings/",
            params={"course_id": course_id, "term_code": "2026-FALL", "status": "ACTIVE"},
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        payload = list_resp.json()["data"]
        assert payload["pagination"]["total"] == 1
        assert payload["items"][0]["id"] == offering_id

        get_resp = await async_client_info.get(
            f"/api/v1/offerings/{offering_id}", headers=auth_headers
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["class_no"] == "01"

        patch_resp = await async_client_info.patch(
            f"/api/v1/offerings/{offering_id}",
            json={"teacher_ids": ["t-2", "t-3"], "status": "COMPLETED"},
            headers=auth_headers,
        )
        assert patch_resp.status_code == 200
        patched = patch_resp.json()["data"]
        assert patched["teacher_ids"] == "t-2,t-3"
        assert patched["status"] == "COMPLETED"

        delete_resp = await async_client_info.delete(
            f"/api/v1/offerings/{offering_id}", headers=auth_headers
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(
            f"/api/v1/offerings/{offering_id}", headers=auth_headers
        )
        assert missing_resp.status_code == 404

    async def test_create_offering_rejects_duplicate_identity(
        self, async_client_info, auth_headers
    ) -> None:
        """当 course_id + term_code + class_no 重复时应返回 409。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS511",
            course_name="Parallel Computing",
            capacity=100,
        )

        first_offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            teacher_ids=[],
            capacity=60,
        )
        assert first_offering_id > 0

        duplicate_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "teacher_ids": [],
                "capacity": 60,
            },
            headers=auth_headers,
        )

        assert duplicate_resp.status_code == 409

    async def test_put_offering_applies_full_replacement_defaults(
        self, async_client_info, auth_headers
    ) -> None:
        """PUT 全量更新时，省略可选字段应回落到 schema 默认值。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS512",
            course_name="Software Testing",
        )

        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="02",
            teacher_ids=["t-9"],
            capacity=88,
        )

        put_resp = await async_client_info.put(
            f"/api/v1/offerings/{offering_id}",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "02",
            },
            headers=auth_headers,
        )

        updated = assert_status_and_data(put_resp)
        assert updated["teacher_ids"] == ""
        assert updated["capacity"] == 0
        assert updated["status"] == "ACTIVE"
