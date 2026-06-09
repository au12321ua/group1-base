# 测试报告

## 1. 报告范围

- 测试框架：`pytest` + `pytest-asyncio` + `pytest-cov`
- 测试边界：按 `docs/tests/test-guide.md` 中的 Router、Service、CRUD、Model 分层策略统计。
- 覆盖对象：`auth_service`、`info_service`、`shared`，跨服务场景位于 `tests/cross_service`。

## 2. 参考依据

- `docs/tests/README.md`：测试分类、执行命令、覆盖率目标。
- `docs/tests/test-guide.md`：命名、标记、fixture、异步测试、错误响应与 CI 约束。
- `docs/TASK_BREAKDOWN.md`：QA Phase 0-3 测试职责和全量集成测试目标。
- `docs/require-spec/validation_matrices/`：认证权限、用户回收站、基础信息数据供给、审计非功能需求矩阵。

## 3. 测试分类汇总

| 范围 | 用例数 | 说明 |
|------|--------|------|
| Auth Service | 79 | 认证 API、内部接口、JWT、安全、CRUD、Service 逻辑 |
| Info Service | 251 | 用户、课程、开课、排课、校历、基础信息、文件、审计、回收站、数据供给 |
| Shared | 55 | 共享数据库、错误处理、路由挂载、安全上下文 |
| Cross Service | 1 | Auth 与 Info 联动的用户生命周期场景 |
| Smoke / Infra | 16 | App、OpenAPI、DB、工具函数基础设施验证 |
| 合计 | 402 | pytest collection 结果 |

## 4. 本地执行记录

| 命令 | 结果 | 备注 |
|------|------|------|
| `UV_CACHE_DIR=/tmp/uv-cache uv run pytest --collect-only -qq` | 通过 | 收集到 402 条测试样例，耗时约 9.24s |
| `UV_CACHE_DIR=/tmp/uv-cache uv run pytest --cov=auth_service --cov=info_service --cov=shared --cov-report=term-missing` | 未完成 | 当前受限沙箱中卡在 `tests/auth_service/test_auth_api.py::TestAuthAPI::test_internal_create_login_me_and_verify`，已终止 |
| `UV_CACHE_DIR=/tmp/uv-cache BCRYPT_COST_FACTOR=4 timeout 60 uv run pytest tests/auth_service/test_auth_api.py::TestAuthAPI::test_internal_create_login_me_and_verify -vv -s` | 超时 | 降低 bcrypt cost 后仍在该 Auth API 集成用例处超时，需在本机或 CI 环境复验 |

说明：测试样例清单来自 pytest collection，能够反映当前分支可被 pytest 发现的完整测试集合。当前环境没有产出可信覆盖率结果，因此覆盖率应以后续 CI 或本机 Docker/非沙箱环境运行结果为准。

## 5. 全部测试样例

以下列表按测试文件分组，条目使用 pytest nodeid，便于直接复制运行。

### tests/auth_service/test_auth_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_auth_api.py::TestAuthAPI::test_internal_create_login_me_and_verify` |
| 2 | `tests/auth_service/test_auth_api.py::TestAuthAPI::test_service_login` |
| 3 | `tests/auth_service/test_auth_api.py::TestAuthAPI::test_refresh_and_logout` |
| 4 | `tests/auth_service/test_auth_api.py::TestAuthAPI::test_change_password_flow` |
| 5 | `tests/auth_service/test_auth_api.py::TestAuthAPI::test_internal_user_lifecycle` |
| 6 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_no_token_returns_401[POST-/api/v1/internal/verify-body0]` |
| 7 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_no_token_returns_401[POST-/api/v1/internal/users-body1]` |
| 8 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_no_token_returns_401[POST-/api/v1/internal/users/u1/disable-None]` |
| 9 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_no_token_returns_401[POST-/api/v1/internal/users/u1/enable-None]` |
| 10 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_no_token_returns_401[POST-/api/v1/internal/users/u1/roles-body4]` |
| 11 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_no_token_returns_401[DELETE-/api/v1/internal/users/u1-None]` |
| 12 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_access_token_returns_401[POST-/api/v1/internal/verify-body0]` |
| 13 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_access_token_returns_401[POST-/api/v1/internal/users-body1]` |
| 14 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_access_token_returns_401[POST-/api/v1/internal/users/u2/disable-None]` |
| 15 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_access_token_returns_401[POST-/api/v1/internal/users/u2/enable-None]` |
| 16 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_access_token_returns_401[POST-/api/v1/internal/users/u2/roles-body4]` |
| 17 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_access_token_returns_401[DELETE-/api/v1/internal/users/u2-None]` |
| 18 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_service_token_allows_verify` |
| 19 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_service_token_allows_create_user` |
| 20 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_service_token_allows_disable_enable` |
| 21 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_service_token_allows_sync_roles` |
| 22 | `tests/auth_service/test_auth_api.py::TestInternalEndpointsAuth::test_service_token_allows_delete` |

### tests/auth_service/test_auth_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_auth_service.py::TestAuthServiceLogin::test_login_success` |
| 2 | `tests/auth_service/test_auth_service.py::TestAuthServiceLogin::test_login_wrong_password` |
| 3 | `tests/auth_service/test_auth_service.py::TestAuthServiceLogin::test_login_locks_after_max_failures` |
| 4 | `tests/auth_service/test_auth_service.py::TestAuthServiceLogin::test_logout_and_refresh_flow` |
| 5 | `tests/auth_service/test_auth_service.py::TestAuthServiceLogin::test_refresh_revokes_token_even_without_session` |
| 6 | `tests/auth_service/test_auth_service.py::TestAuthServiceInternal::test_create_disable_enable_delete_user` |
| 7 | `tests/auth_service/test_auth_service.py::TestAuthServiceInternal::test_create_duplicate_user_raises` |
| 8 | `tests/auth_service/test_auth_service.py::TestAuthServiceInternal::test_create_user_invalid_role_id_raises` |
| 9 | `tests/auth_service/test_auth_service.py::TestAuthServiceMisc::test_change_password` |
| 10 | `tests/auth_service/test_auth_service.py::TestAuthServiceMisc::test_service_login` |
| 11 | `tests/auth_service/test_auth_service.py::TestAuthServiceMisc::test_service_login_invalid_credentials` |

### tests/auth_service/test_credential_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_credential_crud.py::TestCredentialCRUD::test_create_and_get_by_user_id_and_username` |
| 2 | `tests/auth_service/test_credential_crud.py::TestCredentialCRUD::test_increment_and_reset_failed_count` |
| 3 | `tests/auth_service/test_credential_crud.py::TestCredentialCRUD::test_lock_and_unlock_account` |
| 4 | `tests/auth_service/test_credential_crud.py::TestCredentialCRUD::test_update_password_and_delete` |

### tests/auth_service/test_exceptions.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_exceptions.py::test_auth_exception_module_reexports_shared_types` |

### tests/auth_service/test_identity_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_identity_service.py::TestIdentityService::test_verify_access_token_returns_user_identity` |
| 2 | `tests/auth_service/test_identity_service.py::TestIdentityService::test_verify_service_token_returns_scope_permissions` |
| 3 | `tests/auth_service/test_identity_service.py::TestIdentityService::test_verify_service_token_parses_space_separated_scope` |

### tests/auth_service/test_models.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_models.py::TestAuthModels::test_user_default_status_is_active` |
| 2 | `tests/auth_service/test_models.py::TestAuthModels::test_credential_default_fields` |
| 3 | `tests/auth_service/test_models.py::TestAuthModels::test_permission_and_role_permission_persistence` |

### tests/auth_service/test_password_policy.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_admin_password_validation_rejects_invalid_inputs[Short1!-at least 10 characters]` |
| 2 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_admin_password_validation_rejects_invalid_inputs[lowercase1!-uppercase]` |
| 3 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_admin_password_validation_rejects_invalid_inputs[UPPERCASE1!-lowercase]` |
| 4 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_admin_password_validation_rejects_invalid_inputs[NoDigits!!-digit]` |
| 5 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_admin_password_validation_rejects_invalid_inputs[NoSpecial12-special character]` |
| 6 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_admin_password_validation_accepts_valid_password` |
| 7 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_non_admin_password_validation_rejects_invalid_inputs[Short1-at least 8 characters]` |
| 8 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_non_admin_password_validation_rejects_invalid_inputs[password-letters and digits]` |
| 9 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_non_admin_password_validation_rejects_invalid_inputs[12345678-letters and digits]` |
| 10 | `tests/auth_service/test_password_policy.py::TestPasswordPolicy::test_non_admin_password_validation_accepts_valid_password` |

### tests/auth_service/test_permission_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_permission_crud.py::TestPermissionCRUD::test_get_by_code_and_role_permissions` |
| 2 | `tests/auth_service/test_permission_crud.py::TestPermissionCRUD::test_get_user_permissions_via_roles` |

### tests/auth_service/test_role_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_role_crud.py::TestRoleCRUD::test_get_by_id` |
| 2 | `tests/auth_service/test_role_crud.py::TestRoleCRUD::test_get_by_code_and_list_active` |
| 3 | `tests/auth_service/test_role_crud.py::TestRoleCRUD::test_assign_and_get_user_roles` |
| 4 | `tests/auth_service/test_role_crud.py::TestRoleCRUD::test_remove_all_roles` |

### tests/auth_service/test_security.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_security.py::TestPasswordHashing::test_hash_and_verify_roundtrip` |
| 2 | `tests/auth_service/test_security.py::TestPasswordHashing::test_verify_wrong_password` |
| 3 | `tests/auth_service/test_security.py::TestAccessToken::test_access_token_payload_fields` |
| 4 | `tests/auth_service/test_security.py::TestAccessToken::test_admin_token_shorter_expiry` |
| 5 | `tests/auth_service/test_security.py::TestAccessToken::test_access_token_expired_raises` |
| 6 | `tests/auth_service/test_security.py::TestRefreshToken::test_refresh_token_type_field` |
| 7 | `tests/auth_service/test_security.py::TestServiceToken::test_service_token_audience_and_scope` |
| 8 | `tests/auth_service/test_security.py::TestVerifyTokenErrors::test_verify_tampered_token_raises` |
| 9 | `tests/auth_service/test_security.py::TestVerifyTokenErrors::test_verify_wrong_secret_raises` |
| 10 | `tests/auth_service/test_security.py::TestRs256Jwt::test_rs256_access_token_roundtrip` |
| 11 | `tests/auth_service/test_security.py::TestRs256Jwt::test_dual_algorithm_verify_hs256_while_signing_rs256` |

### tests/auth_service/test_session_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_session_crud.py::TestSessionCRUD::test_create_end_and_expire_session` |
| 2 | `tests/auth_service/test_session_crud.py::TestSessionCRUD::test_end_session_idempotent` |
| 3 | `tests/auth_service/test_session_crud.py::TestSessionCRUD::test_expire_session_idempotent` |
| 4 | `tests/auth_service/test_session_crud.py::TestSessionCRUD::test_delete_by_user` |

### tests/auth_service/test_token_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/auth_service/test_token_crud.py::TestTokenCRUD::test_create_get_and_revoke` |
| 2 | `tests/auth_service/test_token_crud.py::TestTokenCRUD::test_revoke_all_for_user` |
| 3 | `tests/auth_service/test_token_crud.py::TestTokenCRUD::test_token_stores_hash_not_plaintext` |
| 4 | `tests/auth_service/test_token_crud.py::TestTokenCRUD::test_delete_by_user` |

### tests/cross_service/test_user_lifecycle.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/cross_service/test_user_lifecycle.py::TestCrossServiceUserLifecycle::test_user_lifecycle_syncs_with_auth_service` |

### tests/info_service/test_audit_logs_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_audit_logs_api.py::TestAuditLogsAPI::test_search_audit_logs_enriches_operator_name` |
| 2 | `tests/info_service/test_audit_logs_api.py::TestAuditLogsAPI::test_export_audit_logs_returns_csv` |

### tests/info_service/test_audit_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_audit_service.py::TestAuditService::test_write_and_search` |
| 2 | `tests/info_service/test_audit_service.py::TestAuditService::test_search_by_operator` |
| 3 | `tests/info_service/test_audit_service.py::TestAuditService::test_search_by_target_type` |
| 4 | `tests/info_service/test_audit_service.py::TestAuditService::test_search_by_action` |
| 5 | `tests/info_service/test_audit_service.py::TestAuditService::test_search_empty` |
| 6 | `tests/info_service/test_audit_service.py::TestAuditService::test_export_csv` |

### tests/info_service/test_auth_http_client.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_auth_http_client.py::TestAuthServiceClient::test_acquire_token_posts_credentials_and_sets_expiry` |
| 2 | `tests/info_service/test_auth_http_client.py::TestAuthServiceClient::test_get_token_uses_cache_until_expiry` |
| 3 | `tests/info_service/test_auth_http_client.py::TestAuthServiceClient::test_request_attaches_authorization_header` |
| 4 | `tests/info_service/test_auth_http_client.py::TestAuthServiceClient::test_internal_helpers_prefix_paths` |
| 5 | `tests/info_service/test_auth_http_client.py::TestAuthServiceClient::test_get_auth_service_client_returns_singleton` |

### tests/info_service/test_base_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_base_crud.py::TestBaseCrud::test_get_multi_returns_rows_in_primary_key_order` |

### tests/info_service/test_base_info_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_base_info_api.py::TestBaseInfoAPI::test_base_info_crud_and_category_filter` |
| 2 | `tests/info_service/test_base_info_api.py::TestBaseInfoAPI::test_create_base_info_rejects_duplicate_category_item_code` |
| 3 | `tests/info_service/test_base_info_api.py::TestBaseInfoAPI::test_base_info_admin_only_mutations_reject_non_admin` |
| 4 | `tests/info_service/test_base_info_api.py::TestBaseInfoAPI::test_list_base_info_rejects_invalid_pagination` |

### tests/info_service/test_base_info_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_create_base_info` |
| 2 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_get_base_info` |
| 3 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_get_base_info_not_found` |
| 4 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_get_multi_base_infos` |
| 5 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_get_multi_base_infos_pagination` |
| 6 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_update_base_info` |
| 7 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_delete_base_info` |
| 8 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_delete_base_info_not_found` |
| 9 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_get_by_category` |
| 10 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_get_by_category_pagination` |
| 11 | `tests/info_service/test_base_info_crud.py::TestBaseInfoCRUD::test_get_by_category_empty` |

### tests/info_service/test_base_info_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_create_base_info` |
| 2 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_get_base_info` |
| 3 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_get_base_info_not_found` |
| 4 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_list_base_info` |
| 5 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_list_base_info_by_category` |
| 6 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_list_base_info_empty_category` |
| 7 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_update_base_info` |
| 8 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_patch_base_info` |
| 9 | `tests/info_service/test_base_info_service.py::TestBaseInfoService::test_delete_base_info` |

### tests/info_service/test_calendar_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_calendar_api.py::TestCalendarAPI::test_list_calendars_rejects_invalid_query` |
| 2 | `tests/info_service/test_calendar_api.py::TestCalendarAPI::test_create_calendar_rejects_invalid_payload` |
| 3 | `tests/info_service/test_calendar_api.py::TestCalendarResourceAccess::test_non_admin_cannot_update_calendar` |
| 4 | `tests/info_service/test_calendar_api.py::TestCalendarResourceAccess::test_non_admin_cannot_delete_calendar` |
| 5 | `tests/info_service/test_calendar_api.py::TestCalendarResourceAccess::test_admin_can_update_calendar` |

### tests/info_service/test_calendar_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_create_calendar` |
| 2 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_calendar` |
| 3 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_calendar_not_found` |
| 4 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_multi_calendars` |
| 5 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_multi_calendars_pagination` |
| 6 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_update_calendar` |
| 7 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_delete_calendar` |
| 8 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_delete_calendar_not_found` |
| 9 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_by_term_code` |
| 10 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_by_term_code_not_found` |
| 11 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_by_date` |
| 12 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_by_date_boundary_start` |
| 13 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_by_date_boundary_end` |
| 14 | `tests/info_service/test_calendar_crud.py::TestCalendarCRUD::test_get_by_date_not_found` |

### tests/info_service/test_calendar_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_create_calendar` |
| 2 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_get_calendar` |
| 3 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_get_calendar_not_found` |
| 4 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_list_calendars` |
| 5 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_update_calendar` |
| 6 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_patch_calendar` |
| 7 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_delete_calendar` |
| 8 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_get_calendar_by_term` |
| 9 | `tests/info_service/test_calendar_service.py::TestCalendarService::test_get_calendar_by_term_not_found` |

### tests/info_service/test_classroom_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_classroom_api.py::TestClassroomAPI::test_classroom_crud_and_filters` |
| 2 | `tests/info_service/test_classroom_api.py::TestClassroomAPI::test_create_classroom_rejects_duplicate_room_no` |
| 3 | `tests/info_service/test_classroom_api.py::TestClassroomAPI::test_patch_classroom_rejects_duplicate_room_no` |
| 4 | `tests/info_service/test_classroom_api.py::TestClassroomAPI::test_list_classrooms_rejects_invalid_pagination` |

### tests/info_service/test_classroom_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_classroom_crud.py::TestClassroomCrud::test_get_by_room_no_returns_classroom` |
| 2 | `tests/info_service/test_classroom_crud.py::TestClassroomCrud::test_get_multi_applies_filters` |
| 3 | `tests/info_service/test_classroom_crud.py::TestClassroomCrud::test_delete_removes_classroom_row` |

### tests/info_service/test_course_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_course_api.py::TestCourseAPI::test_list_courses_rejects_invalid_query` |
| 2 | `tests/info_service/test_course_api.py::TestCourseAPI::test_create_course_rejects_invalid_payload` |
| 3 | `tests/info_service/test_course_api.py::TestCourseAPI::test_create_course_rejects_code_reuse_after_soft_delete` |
| 4 | `tests/info_service/test_course_api.py::TestCourseAPI::test_course_crud_and_prerequisite_flow` |
| 5 | `tests/info_service/test_course_api.py::TestCourseAPI::test_remove_missing_prerequisite_returns_409` |
| 6 | `tests/info_service/test_course_api.py::TestCourseResourceAccess::test_non_admin_cannot_update_course` |
| 7 | `tests/info_service/test_course_api.py::TestCourseResourceAccess::test_non_admin_cannot_patch_course` |
| 8 | `tests/info_service/test_course_api.py::TestCourseResourceAccess::test_non_admin_cannot_delete_course` |
| 9 | `tests/info_service/test_course_api.py::TestCourseResourceAccess::test_admin_can_update_course` |

### tests/info_service/test_course_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_course_crud.py::TestCourseCrud::test_get_by_course_code_returns_created_course` |
| 2 | `tests/info_service/test_course_crud.py::TestCourseCrud::test_get_by_course_code_excludes_deleted_course_by_default` |
| 3 | `tests/info_service/test_course_crud.py::TestCourseCrud::test_get_by_course_code_can_include_deleted_course` |
| 4 | `tests/info_service/test_course_crud.py::TestCourseCrud::test_get_multi_filters_keyword_and_excludes_deleted_by_default` |
| 5 | `tests/info_service/test_course_crud.py::TestCourseCrud::test_logical_delete_marks_course_deleted_and_inactive` |
| 6 | `tests/info_service/test_course_crud.py::TestCourseCrud::test_can_add_list_and_remove_prerequisite` |
| 7 | `tests/info_service/test_course_crud.py::TestCourseCrud::test_add_prerequisite_rejects_self_reference` |

### tests/info_service/test_course_management_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_update_offering_updates_non_identity_fields` |
| 2 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_ensure_required_courses_exist_uses_bulk_lookup` |
| 3 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_create_course_rejects_duplicate_code` |
| 4 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_update_course_rejects_duplicate_code` |
| 5 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_create_schedule_rejects_conflict` |
| 6 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_update_schedule_rejects_conflict_when_identity_changes` |
| 7 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_delete_schedule_not_found_raises` |
| 8 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_replace_teachers_normalizes_and_replaces_existing_assignments` |
| 9 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_add_teachers_deduplicates_existing_assignments` |
| 10 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_assign_teacher_updates_existing_role` |
| 11 | `tests/info_service/test_course_management_service.py::TestCourseManagementService::test_remove_teacher_not_found_raises` |

### tests/info_service/test_data_provision_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_data_provision_api.py::TestDataProvisionAPI::test_list_teachers_and_candidate_students` |
| 2 | `tests/info_service/test_data_provision_api.py::TestDataProvisionAPI::test_get_calendars` |
| 3 | `tests/info_service/test_data_provision_api.py::TestDataProvisionAPI::test_get_calendars_empty` |
| 4 | `tests/info_service/test_data_provision_api.py::TestDataProvisionAPI::test_list_training_programs_supports_filters` |

### tests/info_service/test_data_provision_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_data_provision_service.py::TestDataProvisionService::test_list_teachers_and_candidate_students_filter_by_role_and_status` |
| 2 | `tests/info_service/test_data_provision_service.py::TestDataProvisionService::test_list_training_programs_parses_required_course_ids` |
| 3 | `tests/info_service/test_data_provision_service.py::TestDataProvisionService::test_list_teachers_uses_default_pagination` |

### tests/info_service/test_deps.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_deps.py::TestGetCurrentUser::test_returns_identity_context_with_valid_headers` |
| 2 | `tests/info_service/test_deps.py::TestGetCurrentUser::test_raises_when_user_id_missing` |
| 3 | `tests/info_service/test_deps.py::TestGetCurrentUser::test_raises_when_role_missing` |
| 4 | `tests/info_service/test_deps.py::TestGetCurrentUser::test_empty_permissions_when_none` |
| 5 | `tests/info_service/test_deps.py::TestGetCurrentUser::test_empty_permissions_when_empty_string` |
| 6 | `tests/info_service/test_deps.py::TestGetCurrentUser::test_default_request_id_when_missing` |

### tests/info_service/test_file_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_file_api.py::TestFileAPI::test_file_upload_metadata_download_and_delete` |
| 2 | `tests/info_service/test_file_api.py::TestFileAPI::test_file_access_control_and_admin_bypass` |
| 3 | `tests/info_service/test_file_api.py::TestFileAPI::test_upload_file_rejects_disallowed_type` |
| 4 | `tests/info_service/test_file_api.py::TestFileAPI::test_get_missing_file_returns_404` |

### tests/info_service/test_file_resource_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_file_resource_crud.py::TestFileResourceCRUD::test_create_file_resource` |
| 2 | `tests/info_service/test_file_resource_crud.py::TestFileResourceCRUD::test_get_file_resource` |
| 3 | `tests/info_service/test_file_resource_crud.py::TestFileResourceCRUD::test_delete_file_resource` |
| 4 | `tests/info_service/test_file_resource_crud.py::TestFileResourceCRUD::test_get_by_owner` |
| 5 | `tests/info_service/test_file_resource_crud.py::TestFileResourceCRUD::test_get_by_owner_empty` |

### tests/info_service/test_file_storage_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_upload_file_success` |
| 2 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_upload_file_disallowed_type` |
| 3 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_upload_file_oversize` |
| 4 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_upload_file_invalid_chars_in_type` |
| 5 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_get_file_success` |
| 6 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_get_file_not_found` |
| 7 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_delete_file_owner` |
| 8 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_delete_file_not_owner` |
| 9 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_delete_file_admin_bypass` |
| 10 | `tests/info_service/test_file_storage_service.py::TestFileStorageService::test_delete_file_not_found` |

### tests/info_service/test_offering_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_offering_api.py::TestOfferingAPI::test_offering_crud_flow` |
| 2 | `tests/info_service/test_offering_api.py::TestOfferingAPI::test_create_offering_rejects_duplicate_identity` |
| 3 | `tests/info_service/test_offering_api.py::TestOfferingAPI::test_put_offering_applies_full_replacement_defaults` |
| 4 | `tests/info_service/test_offering_api.py::TestOfferingResourceAccess::test_assigned_teacher_can_update_offering` |
| 5 | `tests/info_service/test_offering_api.py::TestOfferingResourceAccess::test_non_assigned_teacher_cannot_update_offering` |
| 6 | `tests/info_service/test_offering_api.py::TestOfferingResourceAccess::test_student_cannot_delete_offering` |
| 7 | `tests/info_service/test_offering_api.py::TestOfferingResourceAccess::test_admin_can_delete_any_offering` |

### tests/info_service/test_offering_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_offering_crud.py::TestOfferingCrud::test_get_by_course_and_term_returns_matching_rows` |
| 2 | `tests/info_service/test_offering_crud.py::TestOfferingCrud::test_get_multi_applies_supported_filters` |
| 3 | `tests/info_service/test_offering_crud.py::TestOfferingCrud::test_delete_removes_offering_row` |

### tests/info_service/test_offering_route_units.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_offering_route_units.py::TestOfferingRouteHelpers::test_check_offering_access_allows_assigned_teacher` |
| 2 | `tests/info_service/test_offering_route_units.py::TestOfferingRouteHelpers::test_check_offering_access_rejects_unrelated_teacher` |
| 3 | `tests/info_service/test_offering_route_units.py::TestOfferingRouteHelpers::test_enrich_offering_fetches_course_fields` |
| 4 | `tests/info_service/test_offering_route_units.py::TestOfferingRoutes::test_list_offerings_returns_paginated_enriched_items` |
| 5 | `tests/info_service/test_offering_route_units.py::TestOfferingRoutes::test_create_offering_logs_success` |
| 6 | `tests/info_service/test_offering_route_units.py::TestOfferingRoutes::test_get_offering_returns_enriched_response` |
| 7 | `tests/info_service/test_offering_route_units.py::TestOfferingRoutes::test_update_offering_logs_success` |
| 8 | `tests/info_service/test_offering_route_units.py::TestOfferingRoutes::test_patch_offering_logs_success` |
| 9 | `tests/info_service/test_offering_route_units.py::TestOfferingRoutes::test_delete_offering_logs_success` |

### tests/info_service/test_recycle_bin_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_recycle_bin_api.py::TestRecycleBinAPI::test_recycle_bin_flow` |
| 2 | `tests/info_service/test_recycle_bin_api.py::TestRecycleBinAPI::test_batch_physical_delete` |
| 3 | `tests/info_service/test_recycle_bin_api.py::TestRecycleBinRegressions::test_restore_rolls_back_when_auth_enable_fails` |

### tests/info_service/test_recycle_bin_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_recycle_bin_service.py::TestRecycleBinService::test_list_deleted_users` |
| 2 | `tests/info_service/test_recycle_bin_service.py::TestRecycleBinService::test_restore_user` |
| 3 | `tests/info_service/test_recycle_bin_service.py::TestRecycleBinService::test_restore_user_not_found` |
| 4 | `tests/info_service/test_recycle_bin_service.py::TestRecycleBinService::test_restore_user_not_deleted` |
| 5 | `tests/info_service/test_recycle_bin_service.py::TestRecycleBinService::test_physical_delete_user` |
| 6 | `tests/info_service/test_recycle_bin_service.py::TestRecycleBinService::test_physical_delete_user_not_deleted` |
| 7 | `tests/info_service/test_recycle_bin_service.py::TestRecycleBinService::test_batch_physical_delete` |

### tests/info_service/test_reexports.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_reexports.py::test_info_exception_module_reexports_shared_types` |
| 2 | `tests/info_service/test_reexports.py::test_audit_log_crud_module_reexports_shared_symbols` |

### tests/info_service/test_schedule_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_schedule_api.py::TestScheduleAPI::test_schedule_crud_and_teacher_assignment_flow` |
| 2 | `tests/info_service/test_schedule_api.py::TestScheduleAPI::test_create_schedule_rejects_invalid_period_range` |
| 3 | `tests/info_service/test_schedule_api.py::TestScheduleAPI::test_patch_schedule_can_change_offering` |
| 4 | `tests/info_service/test_schedule_api.py::TestScheduleAPI::test_assign_teacher_rejects_path_body_mismatch` |
| 5 | `tests/info_service/test_schedule_api.py::TestScheduleAPI::test_list_schedules_rejects_invalid_pagination` |
| 6 | `tests/info_service/test_schedule_api.py::TestScheduleAPI::test_update_schedule_rejects_conflict_after_identity_change` |
| 7 | `tests/info_service/test_schedule_api.py::TestScheduleAPI::test_remove_teacher_returns_404_when_assignment_missing` |
| 8 | `tests/info_service/test_schedule_api.py::TestScheduleResourceAccess::test_assigned_teacher_can_update_schedule` |
| 9 | `tests/info_service/test_schedule_api.py::TestScheduleResourceAccess::test_non_assigned_teacher_cannot_update_schedule` |
| 10 | `tests/info_service/test_schedule_api.py::TestScheduleResourceAccess::test_student_cannot_delete_schedule` |
| 11 | `tests/info_service/test_schedule_api.py::TestScheduleResourceAccess::test_non_assigned_cannot_manage_teachers` |
| 12 | `tests/info_service/test_schedule_api.py::TestScheduleResourceAccess::test_admin_can_delete_schedule` |

### tests/info_service/test_schedule_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_schedule_crud.py::TestScheduleCrud::test_get_by_offering_returns_sorted_rows` |
| 2 | `tests/info_service/test_schedule_crud.py::TestScheduleCrud::test_check_conflict_detects_overlapping_periods` |

### tests/info_service/test_schedule_route_units.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_schedule_route_units.py::TestScheduleRouteHelpers::test_enrich_schedule_fetches_related_names` |
| 2 | `tests/info_service/test_schedule_route_units.py::TestScheduleRouteHelpers::test_enrich_teacher_assignment_fetches_name` |
| 3 | `tests/info_service/test_schedule_route_units.py::TestScheduleRouteHelpers::test_teacher_assignment_list_response_uses_item_count` |
| 4 | `tests/info_service/test_schedule_route_units.py::TestScheduleRouteHelpers::test_check_schedule_access_allows_assigned_teacher` |
| 5 | `tests/info_service/test_schedule_route_units.py::TestScheduleRouteHelpers::test_check_schedule_access_rejects_unrelated_user` |
| 6 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_list_schedules_returns_paginated_enriched_items` |
| 7 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_create_schedule_logs_success` |
| 8 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_get_schedule_returns_enriched_response` |
| 9 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_update_schedule_logs_success` |
| 10 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_patch_schedule_logs_success` |
| 11 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_delete_schedule_logs_success` |
| 12 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_list_teachers_returns_paginated_enriched_items` |
| 13 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_replace_teachers_logs_success` |
| 14 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_add_teachers_logs_success` |
| 15 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_assign_teacher_logs_success` |
| 16 | `tests/info_service/test_schedule_route_units.py::TestScheduleRoutes::test_remove_teacher_logs_success` |

### tests/info_service/test_security_utils.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_security_utils.py::TestParsePermissionsHeader::test_returns_empty_list_when_header_missing` |
| 2 | `tests/info_service/test_security_utils.py::TestParsePermissionsHeader::test_ignores_blank_items_and_trims_spaces` |
| 3 | `tests/info_service/test_security_utils.py::TestCheckResourceAccess::test_admin_role_has_full_access` |
| 4 | `tests/info_service/test_security_utils.py::TestCheckResourceAccess::test_owner_can_access_own_resource` |
| 5 | `tests/info_service/test_security_utils.py::TestCheckResourceAccess::test_teacher_in_assignment_can_access` |
| 6 | `tests/info_service/test_security_utils.py::TestCheckResourceAccess::test_unrelated_user_cannot_access` |

### tests/info_service/test_training_program_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_training_program_api.py::TestTrainingProgramAPI::test_training_program_crud_flow` |
| 2 | `tests/info_service/test_training_program_api.py::TestTrainingProgramAPI::test_create_training_program_rejects_unknown_course` |
| 3 | `tests/info_service/test_training_program_api.py::TestTrainingProgramResourceAccess::test_non_admin_cannot_update_training_program` |
| 4 | `tests/info_service/test_training_program_api.py::TestTrainingProgramResourceAccess::test_non_admin_cannot_delete_training_program` |
| 5 | `tests/info_service/test_training_program_api.py::TestTrainingProgramResourceAccess::test_admin_can_update_training_program` |

### tests/info_service/test_training_program_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_training_program_crud.py::TestTrainingProgramCrud::test_get_by_program_code_returns_program` |
| 2 | `tests/info_service/test_training_program_crud.py::TestTrainingProgramCrud::test_get_by_major_can_filter_grade` |
| 3 | `tests/info_service/test_training_program_crud.py::TestTrainingProgramCrud::test_get_multi_applies_filters` |

### tests/info_service/test_user_api.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_user_api.py::TestUserAPI::test_user_crud_flow` |
| 2 | `tests/info_service/test_user_api.py::TestUserAPI::test_create_user_rejects_duplicates` |
| 3 | `tests/info_service/test_user_api.py::TestUserAPI::test_delete_user_rolls_back_when_auth_sync_fails` |
| 4 | `tests/info_service/test_user_api.py::TestUserAPI::test_user_routes_enforce_auth_and_validation` |
| 5 | `tests/info_service/test_user_api.py::TestUserAPI::test_batch_import_users_returns_partial_result` |
| 6 | `tests/info_service/test_user_api.py::TestUserResourceAccess::test_non_admin_can_view_own_profile` |
| 7 | `tests/info_service/test_user_api.py::TestUserResourceAccess::test_non_admin_cannot_view_other_profile` |
| 8 | `tests/info_service/test_user_api.py::TestUserResourceAccess::test_admin_can_view_any_profile` |
| 9 | `tests/info_service/test_user_api.py::TestUserResourceAccess::test_non_admin_cannot_update_other_profile` |
| 10 | `tests/info_service/test_user_api.py::TestUserResourceAccess::test_non_admin_can_update_own_profile` |
| 11 | `tests/info_service/test_user_api.py::TestUserResourceAccess::test_non_admin_cannot_delete_users` |
| 12 | `tests/info_service/test_user_api.py::TestUserResourceAccess::test_admin_can_delete_users` |

### tests/info_service/test_user_crud.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_get_by_id` |
| 2 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_get_by_id_not_found` |
| 3 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_get_by_user_no` |
| 4 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_get_by_username` |
| 5 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_create_user` |
| 6 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_update_user` |
| 7 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_get_multi_pagination` |
| 8 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_get_multi_keyword` |
| 9 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_get_multi_include_deleted` |
| 10 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_logical_delete` |
| 11 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_restore` |
| 12 | `tests/info_service/test_user_crud.py::TestUserInfoCRUD::test_physical_delete` |
| 13 | `tests/info_service/test_user_crud.py::TestUserProfileCRUD::test_create_profile` |
| 14 | `tests/info_service/test_user_crud.py::TestUserProfileCRUD::test_get_by_user_id` |
| 15 | `tests/info_service/test_user_crud.py::TestUserProfileCRUD::test_get_by_user_id_not_found` |
| 16 | `tests/info_service/test_user_crud.py::TestUserProfileCRUD::test_update_profile` |
| 17 | `tests/info_service/test_user_crud.py::TestUserProfileCRUD::test_delete_profile` |

### tests/info_service/test_user_management_service.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_get_user` |
| 2 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_get_user_not_found` |
| 3 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_list_users` |
| 4 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_list_users_keyword` |
| 5 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_update_user` |
| 6 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_patch_user` |
| 7 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_disable_user` |
| 8 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_enable_user` |
| 9 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_create_user` |
| 10 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_create_user_rolls_back_when_auth_create_fails` |
| 11 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_update_user_creates_missing_profile` |
| 12 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_patch_user_creates_missing_profile_and_ignores_role_ids` |
| 13 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_logical_delete_user_rolls_back_when_sync_disable_fails` |
| 14 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_batch_import_users_reports_partial_success` |
| 15 | `tests/info_service/test_user_management_service.py::TestUserManagementService::test_batch_import_users_captures_row_exception` |

### tests/shared/test_database.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/shared/test_database.py::TestCreateGetDb::test_returns_async_generator_function` |
| 2 | `tests/shared/test_database.py::TestCreateGetDb::test_get_db_yields_valid_session` |
| 3 | `tests/shared/test_database.py::TestCreateGetDb::test_session_can_perform_crud` |
| 4 | `tests/shared/test_database.py::TestCreateGetDb::test_session_commit_persists_data` |
| 5 | `tests/shared/test_database.py::TestCreateGetDb::test_session_rollback_discards_changes` |
| 6 | `tests/shared/test_database.py::TestCreateGetDb::test_different_engines_are_independent` |

### tests/shared/test_error_handlers.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/shared/test_error_handlers.py::TestErrorHandlerRegistration::test_import_exists` |
| 2 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[AppError]` |
| 3 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[AuthenticationError]` |
| 4 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[AuthorizationError]` |
| 5 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[ResourceNotFoundError]` |
| 6 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[BusinessRuleError]` |
| 7 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[AccountLockedError]` |
| 8 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[AccountDisabledError]` |
| 9 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_status_code[TokenExpiredError]` |
| 10 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[AppError]` |
| 11 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[AuthenticationError]` |
| 12 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[AuthorizationError]` |
| 13 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[ResourceNotFoundError]` |
| 14 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[BusinessRuleError]` |
| 15 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[AccountLockedError]` |
| 16 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[AccountDisabledError]` |
| 17 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_response_body_has_code_and_message[TokenExpiredError]` |
| 18 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[AppError]` |
| 19 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[AuthenticationError]` |
| 20 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[AuthorizationError]` |
| 21 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[ResourceNotFoundError]` |
| 22 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[BusinessRuleError]` |
| 23 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[AccountLockedError]` |
| 24 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[AccountDisabledError]` |
| 25 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_errors_field[TokenExpiredError]` |
| 26 | `tests/shared/test_error_handlers.py::TestAppExceptionToApiResponse::test_unknown_app_error_returns_500` |

### tests/shared/test_main_wiring.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/shared/test_main_wiring.py::TestAuthRouterRegistration::test_v1_auth_login_route_exists` |
| 2 | `tests/shared/test_main_wiring.py::TestAuthRouterRegistration::test_v1_auth_refresh_route_exists` |
| 3 | `tests/shared/test_main_wiring.py::TestAuthRouterRegistration::test_v1_auth_me_route_exists` |
| 4 | `tests/shared/test_main_wiring.py::TestInfoRouterRegistration::test_v1_users_route_exists` |
| 5 | `tests/shared/test_main_wiring.py::TestInfoRouterRegistration::test_v1_courses_route_exists` |
| 6 | `tests/shared/test_main_wiring.py::TestInfoRouterRegistration::test_v1_schedules_route_exists` |
| 7 | `tests/shared/test_main_wiring.py::TestLifespan::test_auth_app_has_lifespan` |
| 8 | `tests/shared/test_main_wiring.py::TestLifespan::test_info_app_has_lifespan` |
| 9 | `tests/shared/test_main_wiring.py::TestErrorHandlerRegistration::test_auth_app_has_error_handlers` |
| 10 | `tests/shared/test_main_wiring.py::TestErrorHandlerRegistration::test_info_app_has_error_handlers` |

### tests/shared/test_security.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/shared/test_security.py::TestIdentityHeaderDependencies::test_get_current_user_id_success` |
| 2 | `tests/shared/test_security.py::TestIdentityHeaderDependencies::test_get_current_user_id_missing_raises` |
| 3 | `tests/shared/test_security.py::TestIdentityHeaderDependencies::test_get_current_user_role_success` |
| 4 | `tests/shared/test_security.py::TestIdentityHeaderDependencies::test_get_current_user_role_missing_raises` |
| 5 | `tests/shared/test_security.py::TestIdentityHeaderDependencies::test_get_current_user_permissions_trimmed` |
| 6 | `tests/shared/test_security.py::TestIdentityHeaderDependencies::test_get_current_user_permissions_empty_returns_list` |
| 7 | `tests/shared/test_security.py::TestPermissionChecker::test_checker_returns_permissions_when_authorized` |
| 8 | `tests/shared/test_security.py::TestPermissionChecker::test_checker_raises_when_permission_missing` |
| 9 | `tests/shared/test_security.py::TestPermissionChecker::test_checker_raises_when_permissions_none` |
| 10 | `tests/shared/test_security.py::TestIdentityContext::test_has_permission_true` |
| 11 | `tests/shared/test_security.py::TestIdentityContext::test_has_permission_false` |
| 12 | `tests/shared/test_security.py::TestIdentityContext::test_has_any_permission_true` |
| 13 | `tests/shared/test_security.py::TestIdentityContext::test_has_any_permission_false` |

### tests/test_infra.py

| # | pytest nodeid |
|---|---------------|
| 1 | `tests/test_infra.py::TestAuthClient::test_app_is_accessible` |
| 2 | `tests/test_infra.py::TestAuthClient::test_openapi_schema` |
| 3 | `tests/test_infra.py::TestInfoClient::test_app_is_accessible` |
| 4 | `tests/test_infra.py::TestInfoClient::test_openapi_schema` |
| 5 | `tests/test_infra.py::TestAuthDB::test_create_and_read_user` |
| 6 | `tests/test_infra.py::TestAuthDB::test_create_credential` |
| 7 | `tests/test_infra.py::TestInfoDB::test_create_and_read_user` |
| 8 | `tests/test_infra.py::TestInfoDB::test_create_course` |
| 9 | `tests/test_infra.py::TestAuditDB::test_create_audit_log` |
| 10 | `tests/test_infra.py::TestUtils::test_build_identity_headers_defaults` |
| 11 | `tests/test_infra.py::TestUtils::test_build_identity_headers_custom` |
| 12 | `tests/test_infra.py::TestUtils::test_build_auth_header` |
| 13 | `tests/test_infra.py::TestUtils::test_make_user_payload_defaults` |
| 14 | `tests/test_infra.py::TestUtils::test_make_user_payload_custom` |
| 15 | `tests/test_infra.py::TestUtils::test_make_course_payload_defaults` |
| 16 | `tests/test_infra.py::TestUtils::test_make_course_payload_custom` |
