from __future__ import annotations

import os
import pickle
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

_INIT_LOCK = threading.Lock()
_INITIALIZED = False


def _resolve_db_path() -> Path:
    custom_path = os.getenv("SOFT_RESIGN_SQLITE_PATH", "").strip()
    if custom_path:
        return Path(custom_path).expanduser().resolve()
    backend_dir = Path(__file__).resolve().parents[2]
    return backend_dir / "data" / "soft_resign.sqlite3"


DB_PATH = _resolve_db_path()


def _schema_sql() -> str:
    return """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  phone TEXT UNIQUE,
  email TEXT UNIQUE,
  wechat_open_id TEXT UNIQUE,
  weibo_open_id TEXT UNIQUE,
  payload BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS forum_boards (
  id TEXT PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  category TEXT NOT NULL,
  market TEXT,
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  payload BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
  id TEXT PRIMARY KEY,
  board_id TEXT NOT NULL,
  author_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  payload BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL,
  author_id TEXT NOT NULL,
  parent_comment_id TEXT,
  created_at TEXT NOT NULL,
  payload BLOB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_posts_board ON posts(board_id);

CREATE TABLE IF NOT EXISTS post_likes (
  post_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (post_id, user_id)
);

CREATE TABLE IF NOT EXISTS post_favorites (
  post_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (post_id, user_id)
);

CREATE TABLE IF NOT EXISTS follows (
  follower_id TEXT NOT NULL,
  followee_id TEXT NOT NULL,
  followed_at TEXT NOT NULL,
  PRIMARY KEY (follower_id, followee_id)
);

CREATE TABLE IF NOT EXISTS access_tokens (
  token TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  expires_at TEXT NOT NULL
);
"""


def _ensure_initialized() -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return

    with _INIT_LOCK:
        if _INITIALIZED:
            return
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.executescript(_schema_sql())
            conn.commit()
        _INITIALIZED = True


@contextmanager
def get_connection():
    _ensure_initialized()
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def encode_payload(obj: object) -> sqlite3.Binary:
    return sqlite3.Binary(pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))


def decode_payload(blob: bytes):
    return pickle.loads(blob)
