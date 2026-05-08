from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime, timedelta

PBKDF2_ALGO = "sha256"
PBKDF2_ITERATIONS = 240_000
TOKEN_TTL_HOURS = 24


def utc_now() -> datetime:
    return datetime.now(UTC)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGO,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return (
        f"pbkdf2_{PBKDF2_ALGO}"
        f"${PBKDF2_ITERATIONS}"
        f"${salt.hex()}"
        f"${digest.hex()}"
    )


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algo_label, iterations_str, salt_hex, digest_hex = encoded_hash.split("$")
    except ValueError:
        return False

    if not algo_label.startswith("pbkdf2_"):
        return False

    algo = algo_label.removeprefix("pbkdf2_")
    try:
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac(
        algo,
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(actual, expected)


def generate_access_token() -> str:
    return secrets.token_urlsafe(32)


def token_expire_time() -> datetime:
    return utc_now() + timedelta(hours=TOKEN_TTL_HOURS)


def mask_id_number(id_number: str | None) -> str | None:
    if not id_number:
        return None
    if len(id_number) <= 4:
        return "*" * len(id_number)
    return f"{id_number[:2]}{'*' * (len(id_number) - 4)}{id_number[-2:]}"

