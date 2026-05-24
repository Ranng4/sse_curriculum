# 虚拟 Git 提交记录（课程进度追踪）

> 说明：以下为按课程模块组织的“虚拟提交历史”，用于展示项目推进过程，并非真实仓库 `git log` 输出。

## 提交记录

1. `a18f2c1` - 2026-05-08 09:30  
   `chore: init project skeleton with flask + pydantic`  
   变更：初始化 `backend/app` 分层目录、基础运行入口。

2. `b7d4e99` - 2026-05-08 14:10  
   `feat(auth): implement register/login/basic verification flow`  
   变更：`auth` 路由、认证 service、token 仓储。

3. `c294f71` - 2026-05-09 10:25  
   `feat(profile): add user profile/preferences/privacy endpoints`  
   变更：个人资料、投资偏好、隐私设置接口。

4. `d8ac5fb` - 2026-05-09 17:40  
   `feat(suitability): add risk questionnaire and result service`  
   变更：适当性问卷与风险等级计算。

5. `e2b10af` - 2026-05-10 11:15  
   `feat(forum): add board sections and board CRUD APIs`  
   变更：默认板块种子数据、板块分区与管理接口。

6. `f70ad32` - 2026-05-11 16:00  
   `docs(module1): add user_stories and use_cases drafts`  
   变更：需求文档初稿，沉淀用户故事与交互场景。

7. `0c31e4d` - 2026-05-29 14:35  
   `feat(content): implement posts/comments/likes/favorites/feed/hot-rank/search`  
   变更：新增内容域模型、仓储、服务与 API 路由。

8. `1f94ab6` - 2026-05-29 14:58  
   `feat(social): implement follow/unfollow/fans/stats APIs`  
   变更：新增社交关系仓储、服务、路由，并接入关注流。

9. `2da43c8` - 2026-05-29 15:08  
   `test: add content and social route unit tests`  
   变更：`test_content_routes.py`、`test_social_routes.py`。

10. `3bb5de1` - 2026-05-29 15:20  
    `docs(module2-5): add architecture/ui/api/db/test/install/user guide and ai log`  
    变更：补齐 `architect.md`、`ui_design.md`、`backend_api.md`、`db.md`、`test.md`、`install.md`、`user_guid.md`、`ai.md`、`assign.md`。

11. `4e8d0a2` - 2026-05-29 15:25  
    `docs: add virtual git history and sql schema`  
    变更：新增 `docs/git_commits_virtual.md` 与 `backend/sql/schema.sql`。
