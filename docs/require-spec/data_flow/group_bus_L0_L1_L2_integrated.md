# STSS大组总线图整合版（L0-L2）

## 1. L0（Context）

### 1.1 图示

```mermaid
flowchart LR
    E1[Student]
    E2[Teacher]
    E3[Academic Administrator]
    E4[System Administrator]
    E5[External AI Service]

    P0((P0: STSS Integrated Teaching Service))

    E1 -->|profile update, plan/course request, forum action, exam entry, score query| P0
    P0 -->|personal profile, timetable, selection result, forum result, exam/score result| E1

    E2 -->|teaching data maintenance, schedule constraints, roster query, exam/grade operation| P0
    P0 -->|teaching timetable, roster/export, exam analytics, grade stats| E2

    E3 -->|window config, override command, moderation command, policy release| P0
    P0 -->|operation status, audit report, risk alert| E3

    E4 -->|security policy, access control policy, system config| P0
    P0 -->|security audit, operation log, health metrics| E4

    P0 -->|recommendation context| E5
    E5 -->|advisory recommendation and explanation| P0
```

### 1.2 解释

#### 1.2.1 作用
- L0用于定义大组系统边界：把6个子系统抽象为一个整体服务 P0。
- L0只表达对外数据交换，不展开内部子系统实现。

#### 1.2.2 参与方与边界
- 外部实体包括学生、教师、教务管理员、系统管理员以及外部AI服务。
- 教务管理员与系统管理员是管理员群体的两种业务身份：前者偏业务运营治理，后者偏平台与安全治理。
- P0内部包含A~F六个子系统协同能力，但在L0不区分子系统。

#### 1.2.3 关键约束
- AI仅提供建议与解释，不直接写入业务主记录。
- 教务与系统管理分离：教务负责业务管控，系统管理员负责安全与平台策略。
- 对外响应遵循最小必要输出原则，避免跨角色越权数据泄露。

#### 1.2.4 与L1关系
- L0中的P0会在L1分解为A~F六个子系统与统一总线能力。
- L0中出现的外部输入输出，必须在L1映射到明确的子系统处理路径。

## 2. L1（Subsystem Decomposition）

### 2.1 图示

#### 2.1.1 整体关联图

```mermaid
flowchart LR
    %% External entities
    E1[Student/Teacher/Admin]
    AI[AI Service]

    %% Unified access and bus
    BUS{{P1 Unified Gateway and Integration Bus}}

    %% Six subsystems
    AUTH((Auth Service))
    A((P2 A Information Management))
    B((P3 B Automatic Course Arrangement))
    C((P4 C Smart Course Selection))
    D((P5 D Discussion Forum))
    E((P6 E Online Testing))
    F((P7 F Score Management))

    %% Shared stores
    D1[(D1 Master Data Hub)]
    D2[(D2 Cross-system Audit and Trace Log)]

    %% User access through unified gateway/bus
    E1 -->|requests| BUS

    BUS --> A
    BUS --> B
    BUS --> C
    BUS --> D
    BUS --> E
    BUS --> F
    BUS -->|Forward Auth Request| AUTH
    AUTH -->|access, refresh token| BUS

    A -->|user, course, term, training program master data| D1
    D1 --> A


    %% AI isolated through C subsystem
    C -->|advisory prompt context| AI
    AI -->|ranked suggestions and explanations| C

    %% Audit
    A --> D2
    B --> D2
    C --> D2
    D --> D2
    E --> D2
    F --> D2

    %% Result back to users
    B -->|teaching timetable/query export| BUS
    C -->|selection result/timetable| BUS
    D -->|forum views/search results| BUS
    E -->|exam status/result views| BUS
    F -->|grade query/analytics reports| BUS

    BUS --> E1
```

#### 2.1.2 主链路数据流图

```mermaid
flowchart LR
    A((A Information Management))
    B((B Automatic Course Arrangement))
    C((C Smart Course Selection))
    E((E Online Testing))
    F((F Score Management))
    D((D Discussion Forum))

    %% Mainline-1: A -> B -> C
    A -->|teacher/course/calendar/classroom baseline| B
    B -->|published timetable and conflict constraints| C

    %% Mainline-2: A -> C -> F
    A -->|student profile and training plan baseline| C
    C -->|final enrollment roster for forum scope check| D
    C -->|selected-course roster and exam eligibility scope| E
    C -->|enrollment records and course-taking relation| F

    %% Mainline-3: E -> F
    E -->|exam score records and scoring basis| F

    %% Mainline-4: D -> F (extended analytics)
    D -->|learning interaction metrics| F

    %% Mainline-5: optional feedback to C
    F -->|credit progress and pass status| C
```

#### 2.1.3 主链路触发条件标注图

```mermaid
flowchart LR
    A((A))
    B((B))
    C((C))
    D((D))
    E((E))
    F((F))

    A -->|T1: 基础数据发布后| B
    B -->|T2: 课表发布后| C
    C -->|T3: 选课名单发布后| D
    C -->|T4: 选课窗口结束或名单冻结后| E
    C -->|T5: 选课结果确认后| F
    E -->|T6: 考试提交并评分完成后| F
    D -->|T7: 统计周期结束后| F
    F -->|T8: 成绩发布后| C
```

### 2.2 解释

#### 2.2.1 分解原则
- L1将L0中的P0分解为统一入口总线 + 6个业务子系统。
- 统一入口总线负责鉴权、路由编排、限流与审计聚合。
- 各业务子系统通过请求header读取uid与role进行业务处理，不重复做登录鉴权。
- 跨组数据流尽量通过标准接口或事件方式传递，降低点对点耦合。

#### 2.2.2 关键主链路
- 主链路图（2.1.2）已完整表达跨子系统业务主线，整体关联图（2.1.1）不再重复绘制同一批跨系统连线。
- 核心链路可归纳为三段：
1. A -> B -> C（基础数据供给与排课结果驱动选课）。
2. C -> D/E/F（选课结果复用到论坛、考试与成绩）。
3. E/D -> F（考试成绩与互动指标汇聚分析）。
- 可选闭环：F -> C 回传学分进展与通过状态，用于推荐优化与培养方案提示。

#### 2.2.3 总线化价值
- 降低耦合：外部实体统一接入BUS，子系统独立演进。
- 提升可治理性：统一限流、审计、告警、链路追踪。
- 便于扩展：未来新增子系统或外部服务只需接入总线层。

#### 2.2.4 实施注意点
- 必须统一跨组ID字典：UserId、CourseId、ClassId、TermId、PlanId、ExamId、ScoreId。
- 必须统一数据状态语义：Draft、Published、Archived。
- 必须统一事件可靠性策略：幂等键、重试、死信与回放机制。
- AI输出保持建议属性，禁止绕过业务规则直接落库。
- 业务权限判定规则由各子系统按role映射实现，避免把子系统授权策略耦合在A组。

## 3. L2（Subsystem Internal Data Flow）

### 3.1 L2 合约表（统一口径）

| L1过程 | L2子过程ID范围 | 关键输入 | 关键输出 | 主要读写存储 | 规则责任方 | 上下游交接 |
|---|---|---|---|---|---|---|
| P2 A信息管理 | P2.1-P2.5 | 用户/课程/权限维护请求 | 主数据快照、权限变更事件 | 主数据Hub、审计日志 | A规则引擎 | -> B/C/F |
| P3 B自动排课 | P3.1-P3.5 | 教学资源、排课规则、手工调课命令 | 已发布课表、冲突约束 | 资源库、版本库、规则库、审计日志 | B排课规则引擎 | -> C |
| P4 C智能选课 | P4.1-P4.6 | 培养方案、检索条件、选退课请求、AI建议请求 | 选课结果、名单发布、AI解释 | 培养方案库、开课库、选课记录库、审计日志 | C选课规则引擎 | -> D/E/F |
| P5 D讨论论坛 | P5.1-P5.5 | 公告/发帖/回帖/审核/检索请求 | 帖子结果、检索结果、互动指标 | 帖子库、统计库、审计日志 | D内容治理规则 | -> F |
| P6 E在线测试 | P6.1-P6.5 | 题库管理、组卷请求、答题提交 | 测试结果、评分记录、分析数据 | 题库、试卷库、答题库、分析库、审计日志 | E考试规则引擎 | -> F |
| P7 F成绩管理 | P7.1-P7.5 | 成绩录入/修改、成绩查询、上游融合数据 | 成绩统计、学分进度反馈 | 成绩库、统计库、审计日志 | F成绩治理规则 | -> C（可选闭环） |

### 3.2 各子系统 L2 分解（图示与解释）

#### 3.2.1 A 信息管理（P2）

##### 图示

```mermaid
flowchart LR
    BUS[统一网关/总线]
    D1[(D1 主数据Hub)]
    D2[(D2 跨系统审计日志)]
    MQ{{事件总线}}
    BCF[下游子系统 B/C/F]

    P21((P2.1 请求解析与鉴权上下文))
    P22((P2.2 用户与档案维护))
    P23((P2.3 课程校历培养方案维护))
    P24((P2.4 权限变更与回收站处理))
    P25((P2.5 主数据快照发布与审计写入))

    BUS -->|资料维护请求| P21
    P21 --> P22
    P21 --> P23
    P21 --> P24

    P22 -->|用户与档案变更| D1
    P23 -->|课程/校历/培养方案变更| D1
    P24 -->|权限映射/逻辑删除恢复| D1

    P22 --> P25
    P23 --> P25
    P24 --> P25
    P25 -->|审计记录| D2
    P25 -->|主数据快照/权限事件| MQ
    MQ -->|标准化数据投递| BCF
```

##### 解释
- 输入：资料维护请求进入 P2.1，完成上下文解析后分流到用户、课程和权限处理链路。
- 处理：P2.2-P2.4 分别完成主数据维护、权限变更与回收站语义处理。
- 输出：P2.5 统一写入审计，并通过事件总线发布标准主数据快照供 B/C/F 消费。
- 治理点：写路径包含校验、持久化、审计三个环节，满足 L2 治理约束。

#### 3.2.2 B 自动排课（P3）

##### 图示

```mermaid
flowchart LR
    BUS[统一网关/总线]
    D1[(教学资源库)]
    D2[(排课版本库)]
    D3[(约束规则库)]
    D4[(排课审计日志)]
    C[子系统C 智能选课]

    P31((P3.1 资源接入与补丁更新))
    P32((P3.2 规则加载与优先级求解))
    P33((P3.3 自动排课生成))
    P34((P3.4 手工调课与冲突校验))
    P35((P3.5 版本发布与课表下发))

    BUS -->|资源维护/排课命令| P31
    BUS -->|规则配置| P32

    P31 -->|写资源可用性| D1
    P32 -->|读写规则| D3
    D1 --> P33
    D3 --> P33
    P33 -->|草稿课表| D2

    BUS -->|手工调课命令| P34
    D2 --> P34
    D3 --> P34
    P34 -->|更新草稿或发布版| D2
    P34 -->|操作差异日志| D4

    D2 --> P35
    P35 -->|发布课表与冲突约束| C
    P35 -->|发布审计| D4
```

##### 解释
- 输入：资源维护命令、规则配置命令、手工调课命令。
- 处理：P3.1-P3.3 完成资源准备、规则求解和自动排课；P3.4 完成人工调整与冲突校验。
- 输出：P3.5 对外发布课表与冲突约束至 C，并写入发布审计。
- 治理点：自动与手工两条路径均汇聚到版本库，避免发布口径不一致。

#### 3.2.3 C 智能选课（P4）

##### 图示

```mermaid
flowchart LR
    BUS[统一网关/总线]
    AI[外部AI服务]
    D1[(学生与培养方案库)]
    D2[(课程与开课库)]
    D3[(选课记录库)]
    D4[(选课审计日志)]
    DEF[子系统 D/E/F]

    P41((P4.1 培养方案校验))
    P42((P4.2 课程检索与可选集构建))
    P43((P4.3 选退课规则引擎))
    P44((P4.4 并发窗口与限流控制))
    P45((P4.5 AI建议适配与解释))
    P46((P4.6 结果固化与名单发布))

    BUS -->|选课请求/检索请求| P41
    D1 --> P41
    P41 --> P42
    D2 --> P42

    P42 --> P43
    D3 --> P43
    P43 -->|选退课事务结果| D3

    BUS -->|窗口配置/连接上限| P44
    P44 --> P43

    BUS -->|AI咨询请求| P45
    P42 -->|候选课程上下文| P45
    P45 -->|建议上下文| AI
    AI -->|建议与解释| P45
    P45 -->|建议结果 不落库| BUS

    P43 --> P46
    P46 -->|名单发布事件| DEF
    P46 -->|审计记录| D4
```

##### 解释
- 输入：选课/检索请求、窗口与并发控制配置、AI 咨询请求。
- 处理：P4.1-P4.4 完成方案校验、可选集构建、规则引擎判定与窗口限流；P4.5 单独处理 AI 建议。
- 输出：P4.6 固化选课结果并向 D/E/F 发布名单事件，同时写入审计日志。
- 治理点：AI 结果只用于建议展示，不直接落事务库，符合“AI 不直写”原则。

#### 3.2.4 D 讨论论坛（P5）

##### 图示

```mermaid
flowchart LR
    BUS[统一网关/总线]
    D1[(帖子与回帖库)]
    D2[(论坛统计库)]
    D3[(论坛审计日志)]
    F[子系统F 成绩管理]

    P51((P5.1 公告管理))
    P52((P5.2 发帖回帖处理))
    P53((P5.3 内容审核与治理))
    P54((P5.4 全文检索与分页))
    P55((P5.5 互动指标聚合与外发))

    BUS -->|公告请求| P51
    P51 -->|公告写入| D1

    BUS -->|发帖回帖请求| P52
    P52 -->|帖子与回复写入| D1

    BUS -->|审核命令| P53
    P53 -->|状态更新| D1
    P53 -->|审核日志| D3

    BUS -->|检索请求| P54
    D1 -->|索引数据| P54
    P54 -->|检索结果| BUS

    D1 -->|浏览/回复交互数据| P55
    P55 -->|热度与活跃统计| D2
    P55 -->|互动指标事件| F
    P55 -->|统计审计| D3
```

##### 解释
- 输入：公告请求、发帖回帖请求、审核命令、检索请求。
- 处理：P5.1-P5.4 分别承担公告、内容写入、审核治理、全文检索；P5.5 聚合互动指标。
- 输出：论坛读写结果返回总线，互动指标周期性输出给 F。
- 治理点：审核与统计过程均写审计日志，保证内容治理可追踪。

#### 3.2.5 E 在线测试（P6）

##### 图示

```mermaid
flowchart LR
    BUS[统一网关/总线]
    D1[(题库)]
    D2[(试卷库)]
    D3[(答题记录库)]
    D4[(分析结果库)]
    D5[(考试审计日志)]
    F[子系统F 成绩管理]

    P61((P6.1 题库管理))
    P62((P6.2 组卷生成与校验))
    P63((P6.3 答题会话与自动保存))
    P64((P6.4 提交评分与发布策略))
    P65((P6.5 统计分析与结果外发))

    BUS -->|题库维护请求| P61
    P61 -->|题目增删改查| D1

    BUS -->|组卷请求| P62
    D1 --> P62
    P62 -->|生成试卷| D2

    BUS -->|考试进入/答题提交| P63
    D2 --> P63
    P63 -->|进度快照/最终答卷| D3

    D3 --> P64
    P64 -->|评分结果与发布控制| D4
    P64 -->|评分审计| D5

    D4 --> P65
    P65 -->|个人结果/教师报表| BUS
    P65 -->|评分记录与分析数据| F
```

##### 解释
- 输入：题库维护、组卷请求、考试进入与答题提交请求。
- 处理：P6.1-P6.3 完成题库管理、组卷生成、会话与自动保存；P6.4 完成评分与发布控制。
- 输出：P6.5 对内返回个人结果/教师报表，对外向 F 发送评分与分析数据。
- 治理点：评分流程与发布策略分离，避免“计算完成即自动发布”的治理风险。

#### 3.2.6 F 成绩管理（P7）

##### 图示

```mermaid
flowchart LR
    BUS[统一网关/总线]
    CDE[来自 C/D/E 的融合输入]
    D1[(成绩主库)]
    D2[(成绩统计库)]
    D3[(成绩审计日志)]
    C[子系统C 智能选课]

    P71((P7.1 成绩录入与校验))
    P72((P7.2 成绩修改申请与审批))
    P73((P7.3 学生查询与学分核算))
    P74((P7.4 课程级与个人级分析))
    P75((P7.5 结果发布与进度反馈))

    BUS -->|录入与查询请求| P71
    P71 -->|初次成绩写入| D1

    BUS -->|改分请求| P72
    P72 -->|审批后变更| D1
    P72 -->|改分审计| D3

    CDE -->|选课/互动/考试融合数据| P73
    D1 --> P73
    P73 -->|学分与绩点中间结果| P74

    P74 -->|统计分析结果| D2
    P74 -->|分析审计| D3

    D1 --> P75
    D2 --> P75
    P75 -->|成绩查询与分析报表| BUS
    P75 -->|学分进度反馈 可选| C
```

##### 解释
- 输入：录入/改分/查询请求，以及来自 C/D/E 的融合数据。
- 处理：P7.1-P7.4 完成录入、受控改分、学分核算与统计分析。
- 输出：P7.5 统一发布成绩查询与分析报表，并可选回传学分进度至 C。
- 治理点：改分链路独立建模并审计，满足“二次修改可控、可追溯”要求。
