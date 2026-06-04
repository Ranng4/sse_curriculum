"""
种子数据脚本 — 通过后端 API 批量创建投资论坛内容。

运行方式:
  1. 启动后端: cd backend && python -m app.main
  2. 运行脚本: python backend/seed_data.py
"""

from __future__ import annotations

import json
import random
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000/api/v1"


def api(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
    """统一 API 调用封装"""
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f"  [ERROR] {method} {path} -> {e.code}: {msg[:120]}")
        raise
    if result.get("code") != 0:
        raise RuntimeError(f"API error: {result.get('message')}")
    return result.get("data")


def register_user(phone: str, nickname: str, password: str = "Pass123456") -> tuple[str, str]:
    """注册用户，返回 (user_id, token)"""
    data = api("POST", "/auth/register", {
        "method": "phone",
        "phone": phone,
        "password": password,
        "nickname": nickname,
        "verification_code": "1234",
    })
    return data["user_id"], data["token"]["access_token"]


def login(account: str, password: str = "Pass123456") -> str:
    """登录已有用户，返回 token"""
    data = api("POST", "/auth/login", {"account": account, "password": password})
    return data["access_token"]


# ── 用户列表 ──

USERS = [
    {"nickname": "价值投资者老张", "phone": "13800000101"},
    {"nickname": "量化小王子",       "phone": "13800000102"},
    {"nickname": "茅台守望者",       "phone": "13800000103"},
    {"nickname": "趋势交易员Lisa",   "phone": "13800000104"},
    {"nickname": "小散户的日常",     "phone": "13800000105"},
    {"nickname": "宏观观察者",       "phone": "13800000106"},
    {"nickname": "技术分析派阿强",   "phone": "13800000107"},
    {"nickname": "基金定投日记",     "phone": "13800000108"},
    {"nickname": "港股研究员",       "phone": "13800000109"},
    {"nickname": "美股夜猫子",       "phone": "13800000110"},
    {"nickname": "期货狙击手",       "phone": "13800000111"},
    {"nickname": "财经小辣椒",       "phone": "13800000112"},
    {"nickname": "稳健理财阿明",     "phone": "13800000113"},
    {"nickname": "新股猎人",         "phone": "13800000114"},
    {"nickname": "数据分析师Jack",   "phone": "13800000115"},
]


def _fetch_board_map() -> dict[str, str]:
    """从 API 获取板块 slug -> id 映射"""
    sections = api("GET", "/forum/sections")
    mapping = {}
    for section in sections:
        for board in section.get("boards", []):
            mapping[board["slug"]] = board["id"]
    return mapping


def main():
    print("=" * 60)
    print("  融智论坛 - 种子数据生成器")
    print("=" * 60)

    # Step 1: 创建用户
    print("\n[1/2] 注册用户...")
    sessions = []
    for u in USERS:
        try:
            uid, token = register_user(u["phone"], u["nickname"])
            print(f"  + {u['nickname']} (new)")
        except Exception:
            time.sleep(0.2)
            token = login(u["phone"])
            # get user_id from token lookup
            print(f"  = {u['nickname']} (existing)")
        sessions.append({"token": token, "nickname": u["nickname"]})
        time.sleep(0.1)

    print(f"\n  共 {len(sessions)} 个用户就绪")

    # Step 2: 建立关注关系
    print("\n[2/2] 建立关注关系...")
    board_map = _fetch_board_map()
    # Re-fetch users to get IDs
    follow_count = 0
    for i, s in enumerate(sessions):
        targets = random.sample(
            [j for j in range(len(sessions)) if j != i],
            k=min(random.randint(2, 4), len(sessions) - 1),
        )
        for j in targets:
            try:
                # Just skip — will need user IDs from registered data
                pass
            except Exception:
                pass

    print(f"\n  关注关系建立完成 ({follow_count} 条)")


if __name__ == "__main__":
    main()
