# 安装部署文档（模块5交付）

## 1. 环境要求

1. Python 3.13+
2. `uv`（推荐）或 `pip`
3. Windows / Linux / macOS

## 2. 获取项目

```bash
git clone <your-repo-url>
cd soft_resign
```

## 3. 安装依赖

### 方式A（推荐，uv）

```bash
uv sync
```

### 方式B（pip）

```bash
pip install -e .
```

## 4. 启动后端

```bash
cd backend
python -m app.main
```

默认监听：`http://127.0.0.1:8000`

健康检查：

```bash
curl http://127.0.0.1:8000/healthz
```

预期响应：

```json
{"status":"ok"}
```

## 5. 运行测试

```bash
cd backend
uv run python -m unittest -v tests.test_forum_routes tests.test_content_routes tests.test_social_routes
```

## 6. SQLite 持久化说明

系统默认使用 SQLite，首次启动会自动创建数据库文件：

- 默认路径：`backend/data/soft_resign.sqlite3`
- 自定义路径：设置环境变量 `SOFT_RESIGN_SQLITE_PATH`

PowerShell 示例：

```powershell
$env:SOFT_RESIGN_SQLITE_PATH="D:\\data\\soft_resign.sqlite3"
python -m app.main
```

## 7. 常见问题

### 7.1 `Authorization` 报错

- 确认请求头格式为：`Bearer <token>`
- token 来自 `/api/v1/auth/register` 或 `/api/v1/auth/login`

### 7.2 端口占用

- 修改 `backend/app/main.py` 中 `app.run(..., port=8000)` 为其他端口

### 7.3 `uv` 缓存权限问题

- 可设置本地缓存目录再执行：

```bash
set UV_CACHE_DIR=.uv-cache
```
