# 后端接口文档（模块2/3交付）

## 1. 文档说明

- OpenAPI 3.0 模板文件：`docs/openapi.yaml`
- 基础地址：`http://127.0.0.1:8000`
- 统一响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

## 2. 认证方式

- Header：`Authorization: Bearer <access_token>`
- 登录后从 `/api/v1/auth/register` 或 `/api/v1/auth/login` 获取 token。

## 3. 接口分组总览

### 3.1 Auth

1. `POST /api/v1/auth/register` 注册（手机/邮箱/第三方）
2. `POST /api/v1/auth/login` 登录
3. `GET /api/v1/auth/basic-verification` 查询基础认证状态
4. `POST /api/v1/auth/basic-verification` 提交基础认证
5. `GET /api/v1/auth/real-name-verification` 查询实名认证状态
6. `POST /api/v1/auth/real-name-verification` 提交实名认证
7. `GET /api/v1/auth/professional-verification` 查询专业认证状态
8. `POST /api/v1/auth/professional-verification` 提交专业认证

### 3.2 Profile

1. `GET /api/v1/profile/me` 我的资料
2. `PATCH /api/v1/profile/basic` 修改基础资料
3. `PATCH /api/v1/profile/investment-preferences` 修改投资偏好
4. `PATCH /api/v1/profile/privacy-settings` 修改隐私设置
5. `GET /api/v1/profile/{target_user_id}` 查看公开资料

### 3.3 Suitability

1. `GET /api/v1/suitability/questionnaire` 获取风险问卷
2. `POST /api/v1/suitability/submit` 提交问卷
3. `GET /api/v1/suitability/result` 获取评估结果

### 3.4 Forum

1. `GET /api/v1/forum/sections` 分区列表
2. `GET /api/v1/forum/markets|topics|company-research|qa` 分区快捷入口
3. `GET /api/v1/forum/boards` 板块列表（支持筛选）
4. `GET /api/v1/forum/boards/{board_id}` 板块详情
5. `POST /api/v1/forum/boards` 创建板块
6. `PATCH /api/v1/forum/boards/{board_id}` 更新板块
7. `DELETE /api/v1/forum/boards/{board_id}` 删除板块

### 3.5 Content（本次新增）

1. `POST /api/v1/content/posts` 发布帖子
2. `PATCH /api/v1/content/posts/{post_id}` 更新帖子
3. `GET /api/v1/content/posts` 帖子列表（`keyword/stock_code/sort/limit`）
4. `GET /api/v1/content/posts/{post_id}` 帖子详情
5. `POST /api/v1/content/posts/{post_id}/comments` 发表评论
6. `GET /api/v1/content/posts/{post_id}/comments` 评论列表
7. `POST|DELETE /api/v1/content/posts/{post_id}/like` 点赞/取消点赞
8. `POST|DELETE /api/v1/content/posts/{post_id}/favorite` 收藏/取消收藏
9. `GET /api/v1/content/feed` 信息流（支持 `following_only`）
10. `GET /api/v1/content/hot-rank` 热榜
11. `GET /api/v1/content/search/suggest` 搜索联想

### 3.6 Social（本次新增）

1. `POST /api/v1/social/follows/{target_user_id}` 关注用户
2. `DELETE /api/v1/social/follows/{target_user_id}` 取消关注
3. `GET /api/v1/social/follows/me` 我的关注列表
4. `GET /api/v1/social/fans/me` 我的粉丝列表
5. `GET /api/v1/social/stats/me` 我的关注统计

## 4. 典型调用示例

### 4.1 注册并发帖

1. 调用 `POST /api/v1/auth/register` 获取 token
2. 调用 `POST /api/v1/content/posts` 发布帖子

请求示例：

```json
{
  "board_id": "board-id",
  "title": "新能源ETF周观察",
  "content": "关注成交量和资金净流入变化。",
  "post_type": "normal",
  "stock_codes": ["159915"]
}
```

### 4.2 点赞和收藏

1. `POST /api/v1/content/posts/{post_id}/like`
2. `POST /api/v1/content/posts/{post_id}/favorite`

返回中 `metrics` 会体现最新互动计数。

## 5. 错误码约定

1. `400` 参数错误、业务校验失败
2. `401` 鉴权失败或 token 失效
3. `404` 资源不存在
4. `409` 资源冲突（如重复注册、删除有子板块的板块）
