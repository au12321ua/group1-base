# 分支管理策略

> 适用团队：4 开发 + 1 测试，GitHub 托管，Agent 辅助开发。
> 基于 GitHub Flow，保持流程简洁。

---

## 1. 分支模型

```
main  ───○──────────────────────────────○────────────○────
          \                             /            /
           feat/user-import ──○──○──○─┘            /
                                                   /
            feat/course-crud ──○──○──○────────────┘
```

所有分支从 `main` 创建，通过 PR 合并回 `main`，**不设长期存在的 develop 分支**。

### 1.1 分支类型与命名

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat/` | 新功能 | `feat/user-import-endpoint` |
| `fix/` | Bug 修复 | `fix/token-expiry-check` |
| `chore/` | 基础设施、配置、文档 | `chore/ci-setup` |
| `release/` | 发布准备 | `release/v0.1.0` |
| `hotfix/` | 线上紧急修复 | `hotfix/jwt-key-rotation` |

**命名约定**：
- 全部小写，单词间用 `-` 连接
- 简洁描述功能，不超过 5 个词
- 避免 `feat/123` 这样的纯编号命名（如果有 issue，格式为 `feat/123-user-import`）

### 1.2 分支生命周期

```
创建 ──→ 开发 ──→ 推送 ──→ PR ──→ Review ──→ 合并 ──→ 删除
  │                                                    │
  └── 从 main 拉新分支                                  └── 合并后立即删除远程分支
```

---

## 2. main 分支保护规则

在 GitHub 仓库 Settings → Branches 中配置：

| 规则 | 值 |
|------|-----|
| 禁止直接 push 到 main | ✅ 开启 |
| PR 合并前至少 1 人 Approve | ✅ 开启 |
| 合并前 CI 必须通过 | ✅ 开启（待 CI 配置后） |
| 合并前对话必须解决 | ✅ 开启 |
| 合并方式 | Squash Merge（仅允许） |

---

## 3. 开发工作流

### 3.1 日常开发流程

```bash
# 1. 同步最新 main
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feat/xxxx

# 3. 开发 + 小步提交
git add <specific-files>
git commit -m "feat: 用户导入接口增加 CSV 格式校验"

# 4. 本地验证
uv run ruff check .
uv run pytest

# 5. 推送前 rebase main（如有远端变更）
git fetch origin main
git rebase origin/main

# 6. 推送
git push -u origin feat/xxxx

# 7. 创建 PR（使用 gh 或 GitHub 网页）
gh pr create --title "feat: 用户批量导入接口" --body-file .github/pr_body.txt
```

### 3.2 提交信息规范

采用简易 Conventional Commits：

```
<type>: <简短描述>

<详细说明（可选）>
```

| Type | 何时使用 |
|------|----------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `refactor` | 重构（不改变功能） |
| `docs` | 仅文档变更 |
| `test` | 添加/修改测试 |
| `chore` | 构建/配置/依赖 |

示例：
```
feat: 实现 POST /users/import 批量导入接口

- 支持 CSV 格式批量导入
- 跨服务同步 Auth Service 创建认证用户
- 含事务补偿机制
```

### 3.3 Rebase vs Merge

| 场景 | 操作 |
|------|------|
| 功能分支同步 main 最新代码 | `git rebase origin/main`（保持线性历史） |
| 合并 PR 到 main | GitHub 网页端 Squash Merge（一个 PR = 一个提交） |
| 多人协作同一分支 | **禁止** force push 到共享分支 |

> **原则**：只 rebase 你个人的分支。一旦分支被推送到远端并被他人基于其工作，只做 merge。

---

## 4. PR 规范

### 4.1 PR 大小

- 一个 PR 对应一个完整功能或修复
- **推荐**：200-400 行变更，超过 600 行应拆分
- Agent 生成的代码容易偏大，提交前让 Agent 自查是否可以拆分

### 4.2 Review 重点

Reviewer 检查以下内容：

1. **架构合规**：是否遵守 Router → Service → CRUD → Model 单向依赖
2. **安全**：是否有 token 泄露、越权访问、SQL 注入风险
3. **跨服务影响**：Auth/Info 接口变更是否影响对方
4. **测试覆盖**：核心路径和边界条件是否有测试
5. **代码风格**：ruff 是否通过、类型注解是否完整

### 4.3 冲突解决

```bash
# 当 PR 和 main 有冲突时
git checkout feat/xxxx
git fetch origin main
git rebase origin/main

# 解决冲突文件后
git add <resolved-files>
git rebase --continue
git push --force-with-lease   # 只在个人分支上用
```

---

## 5. 发布流程

### 5.1 常规发布

```
1. 从 main 创建 release 分支：release/v0.1.0
2. 更新版本号、CHANGELOG
3. 进行最终测试（全量回归）
4. PR 回 main（Review 通过后合并）
5. 在 main 上打 tag：git tag -a v0.1.0 -m "版本描述"
6. 推送 tag：git push origin v0.1.0
7. 部署对应 tag 的 Docker 镜像
```

### 5.2 紧急修复（Hotfix）

```
main ○ ──→ hotfix/xxx ──→ ○ (hotfix 合并)
     \                     /
      ○ ← 正常开发中的分支也要 rebase 此 hotfix
```

```bash
git checkout main
git checkout -b hotfix/critical-bug
# 修复、提交、推送
git checkout main
git merge --squash hotfix/critical-bug
git tag -a v0.1.1 -m "Hotfix: 修复 JWT 过期判断"
git push origin main --tags
# 其他开发分支 rebase main 获得修复
```

---

## 6. 分支命名速查

```
feat/login-captcha          # 新功能：登录验证码
feat/user-batch-import      # 新功能：用户批量导入
feat/course-offering-crud   # 新功能：课程开课管理
fix/token-revocation        # Bug 修复：令牌撤销逻辑
fix/db-connection-leak      # Bug 修复：数据库连接泄漏
chore/ruff-rules            # 配置：ruff 规则调整
chore/update-readme         # 文档：更新 README
release/v0.1.0              # 发布：版本 0.1.0
hotfix/security-patch       # 紧急修复：安全补丁
```

---

## 7. 测试分支策略

测试人员使用单独的分支管理测试代码：

| 分支 | 用途 |
|------|------|
| `test/integration` | 集成测试编写（不干扰开发） |
| `test/e2e` | 端到端测试脚本 |

测试分支工作流：
1. 测试在 `test/xxx` 分支编写测试
2. 向 `main` 提 PR（Review 后合并）
3. 开发完成的功能分支优先合入 `main`，测试紧随其后

---

## 8. 常见问题

**Q: 不小心在 main 上写了代码怎么办？**
```bash
git stash
git checkout -b feat/xxx
git stash pop
```
然后正常提交推送。

**Q: Agent 生成了大量文件，PR 太大怎么办？**
让 Agent 按功能拆分：先用一个 PR 完成 Model + Schema 定义，再用下一个 PR 完成 Service + CRUD 实现。

**Q: 多人同时修改 shared/ 怎么办？**
shared/ 改动应先沟通，建议由分担基础设施的组员 Review 后合入，其他人再 rebase。
