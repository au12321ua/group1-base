# Information Management 数据库结构说明（描述版）

> 说明：
> - 本文档为结构描述，不包含任何数据库方言的建表 SQL。

## 1. 用户与权限域

### 1.1 users（用户表）
- 主键：`user_id`
- 核心字段：`username`（唯一）、`password_hash`、`name`、`email`、`department`、`status`
- 语义：存储学生、教师、管理员基础信息。

### 1.2 roles（角色表）
- 主键：`role_id`
- 核心字段：`role_name`（唯一）、`description`
- 语义：定义系统角色（如学生、教师、管理员）。

### 1.3 permissions（权限表）
- 主键：`permission_id`
- 核心字段：`permission_name`（唯一）、`resource`、`action`、`description`
- 语义：定义可授权的细粒度权限项。

### 1.4 user_roles（用户-角色关联表）
- 主键：`user_role_id`
- 外键：
  - `user_id` -> `users.user_id`
  - `role_id` -> `roles.role_id`
- 唯一约束：`(user_id, role_id)`
- 语义：用户与角色的多对多关系。

### 1.5 role_permissions（角色-权限关联表）
- 主键：`role_permission_id`
- 外键：
  - `role_id` -> `roles.role_id`
  - `permission_id` -> `permissions.permission_id`
- 唯一约束：`(role_id, permission_id)`
- 语义：角色与权限的多对多关系。

## 2. 课程与开课域

### 2.1 courses（课程定义表）
- 主键：`course_id`
- 核心字段：`course_code`（唯一）、`course_name`、`credits`、`hours`、`assessment_type`、`course_type`、`department`
- 语义：课程静态元数据定义。

### 2.2 course_offerings（课程开设表）
- 主键：`offering_id`
- 外键：`course_id` -> `courses.course_id`
- 核心字段：`semester`、`year`、`section`、`status`
- 唯一约束：`(course_id, year, semester, section)`
- 语义：某门课程在某学年学期和班次的具体开设实例。

### 2.3 course_prerequisites（课程先修关系表）
- 主键：`prerequisite_id`
- 外键：
  - `course_id` -> `courses.course_id`
  - `required_course_id` -> `courses.course_id`
- 唯一约束：`(course_id, required_course_id)`
- 规则语义：禁止 `course_id = required_course_id`（不可自引用）
- 语义：课程与先修课程的依赖关系。

## 3. 排课与教学资源域

### 3.1 classrooms（教室表）
- 主键：`classroom_id`
- 核心字段：`building`、`room_number`、`capacity`、`status`
- 唯一约束：`(building, room_number)`
- 规则语义：`capacity > 0`
- 语义：可用于排课的教室资源。

### 3.2 course_schedules（课程排课表）
- 主键：`schedule_id`
- 外键：
  - `offering_id` -> `course_offerings.offering_id`
  - `classroom_id` -> `classrooms.classroom_id`（可空）
- 核心字段：`day_of_week`、`start_time`、`end_time`
- 规则语义：
  - `day_of_week` 在 1 到 7 之间
  - `end_time > start_time`
- 语义：开课实例在一周中的具体上课安排。

### 3.3 teacher_course_assignments（教师授课分配表）
- 主键：`assignment_id`
- 外键：
  - `teacher_id` -> `users.user_id`
  - `schedule_id` -> `course_schedules.schedule_id`
- 唯一约束：`(teacher_id, schedule_id)`
- 语义：教师与排课记录的多对多关系。

## 4. 选课与成绩域

### 4.1 student_course_enrollments（学生选课关系表）
- 主键：`enrollment_id`
- 外键：
  - `student_id` -> `users.user_id`
  - `offering_id` -> `course_offerings.offering_id`
- 核心字段：`enrollment_status`、`grade`、`grade_status`、`enrollment_date`
- 唯一约束：`(student_id, offering_id)`
- 语义：学生对开课实例的选课记录与成绩状态。

## 5. 关系总览（保持不变）

1. 用户与权限关系
- `users` 与 `roles` 通过 `user_roles` 建立多对多。
- `roles` 与 `permissions` 通过 `role_permissions` 建立多对多。

2. 课程主线关系
- `courses` 与 `course_offerings` 为一对多。
- `course_offerings` 与 `course_schedules` 为一对多。

3. 教学组织关系
- `users(教师)` 与 `course_schedules` 通过 `teacher_course_assignments` 建立多对多。
- `users(学生)` 与 `course_offerings` 通过 `student_course_enrollments` 建立多对多。

4. 资源与依赖关系
- `classrooms` 与 `course_schedules` 为一对多（排课可暂不分配教室）。
- `courses` 与 `courses` 通过 `course_prerequisites` 建立先修依赖有向关系。