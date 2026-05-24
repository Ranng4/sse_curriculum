# 软件使用说明书（模块5交付）

## 1. 产品简介

股票基金投资论坛用于投资交流，支持：

1. 多方式注册与登录
2. 论坛板块浏览
3. 发帖、评论、点赞、收藏
4. 关注用户与查看关注流
5. 风险问卷与个人资料管理

## 2. 角色说明

1. 游客：可浏览公开内容
2. 注册用户：可发帖、评论、互动、关注
3. 管理员（扩展）：可进行板块和内容治理

## 3. 主要功能流程

### 3.1 新用户注册与登录

1. 调用 `POST /api/v1/auth/register` 完成注册
2. 返回 `access_token`
3. 后续请求在 Header 中加入 `Authorization: Bearer <token>`

### 3.2 浏览板块

1. `GET /api/v1/forum/sections` 查看全部分区
2. `GET /api/v1/forum/markets` 等快捷查看具体分区

### 3.3 发布帖子

1. 调用 `POST /api/v1/content/posts`
2. 必填：`board_id`、`title`、`content`
3. 可选：`post_type`、`stock_codes`、`image_urls`

### 3.4 评论与互动

1. 发表评论：`POST /api/v1/content/posts/{post_id}/comments`
2. 点赞：`POST /api/v1/content/posts/{post_id}/like`
3. 取消点赞：`DELETE /api/v1/content/posts/{post_id}/like`
4. 收藏：`POST /api/v1/content/posts/{post_id}/favorite`
5. 取消收藏：`DELETE /api/v1/content/posts/{post_id}/favorite`

### 3.5 关注用户

1. 关注：`POST /api/v1/social/follows/{target_user_id}`
2. 取关：`DELETE /api/v1/social/follows/{target_user_id}`
3. 我的关注：`GET /api/v1/social/follows/me`
4. 我的粉丝：`GET /api/v1/social/fans/me`

### 3.6 查看信息流与热榜

1. 首页流：`GET /api/v1/content/feed`
2. 关注流：`GET /api/v1/content/feed?following_only=true`
3. 热榜：`GET /api/v1/content/hot-rank`
4. 搜索：`GET /api/v1/content/posts?keyword=xxx`
5. 搜索联想：`GET /api/v1/content/search/suggest?q=xxx`

## 4. 常见错误说明

1. `401`：未登录或 token 失效
2. `400`：参数不合法（如 limit 非数字、sort 非法）
3. `404`：资源不存在（帖子、板块、用户）
4. `409`：冲突（重复注册等）

## 5. 使用建议

1. 发帖建议带上 `stock_codes`，便于搜索与聚合。
2. 长文建议使用 `post_type=longform`，实时讨论用 `realtime`。
3. 关注高质量作者后，优先使用 `following_only=true` 查看信息流。
