"""Admin API route tests — content review, user management, analytics.

AI-generated: unit tests for admin moderation endpoints.
"""

from __future__ import annotations

import unittest
from uuid import uuid4

from app.main import create_app


class AdminRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_app().test_client()

    def _assert_ok(self, response, expected_status: int = 200):
        self.assertEqual(response.status_code, expected_status)
        payload = response.get_json()
        self.assertEqual(payload["code"], 0)
        return payload["data"]

    def _auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def _register_user(self, nickname: str) -> tuple[str, str]:
        suffix = uuid4().hex[:9]
        phone = f"139{suffix}"
        data = self._assert_ok(
            self.client.post(
                "/api/v1/auth/register",
                json={
                    "method": "phone",
                    "phone": phone,
                    "password": "Pass123456",
                    "nickname": nickname,
                    "verification_code": "1234",
                },
            ),
            expected_status=201,
        )
        return data["user_id"], data["token"]["access_token"]

    def test_admin_stats(self):
        """Forum stats should return non-zero values after seeding."""
        uid, token = self._register_user("AdminTest")
        data = self._assert_ok(
            self.client.get("/api/v1/admin/stats", headers=self._auth_headers(token))
        )
        self.assertGreaterEqual(data["total_users"], 1)
        self.assertIn("posts_today", data)
        self.assertIn("top_boards", data)

    def test_post_review_flow(self):
        """Approve, flag, and reject a post through admin review."""
        uid, token = self._register_user("Reviewer")

        # Get a board ID first
        market = self._assert_ok(self.client.get("/api/v1/forum/markets"))
        board_id = market["boards"][0]["id"]

        # Create a post
        post = self._assert_ok(
            self.client.post(
                "/api/v1/content/posts",
                headers=self._auth_headers(token),
                json={
                    "board_id": board_id,
                    "title": "Test Post for Review",
                    "content": "This post will be reviewed.",
                },
            ),
            expected_status=201,
        )

        # List posts for review
        posts = self._assert_ok(
            self.client.get("/api/v1/admin/posts", headers=self._auth_headers(token))
        )
        self.assertGreaterEqual(len(posts), 1)

        # Flag the post
        reviewed = self._assert_ok(
            self.client.patch(
                f"/api/v1/admin/posts/{post['id']}",
                headers=self._auth_headers(token),
                json={"action": "flag", "reason": "Suspicious content"},
            )
        )
        self.assertEqual(reviewed["review_status"], "flag")

        # Approve the post
        approved = self._assert_ok(
            self.client.patch(
                f"/api/v1/admin/posts/{post['id']}",
                headers=self._auth_headers(token),
                json={"action": "approve", "reason": "Looks fine"},
            )
        )
        self.assertEqual(approved["review_status"], "approve")

    def test_user_management_flow(self):
        """Warn and unban a user through admin management."""
        _, admin_token = self._register_user("AdminManager")
        target_id, target_token = self._register_user("TargetUser")

        # List users
        users = self._assert_ok(
            self.client.get("/api/v1/admin/users", headers=self._auth_headers(admin_token))
        )
        self.assertGreaterEqual(len(users), 2)

        # Warn the target
        warned = self._assert_ok(
            self.client.patch(
                f"/api/v1/admin/users/{target_id}",
                headers=self._auth_headers(admin_token),
                json={"action": "warn", "reason": "Spam posting"},
            )
        )
        self.assertEqual(warned["user_status"], "warn")

        # Ban the target
        banned = self._assert_ok(
            self.client.patch(
                f"/api/v1/admin/users/{target_id}",
                headers=self._auth_headers(admin_token),
                json={"action": "ban", "reason": "Repeat violation"},
            )
        )
        self.assertEqual(banned["user_status"], "banned")

        # Unban the target
        unbanned = self._assert_ok(
            self.client.patch(
                f"/api/v1/admin/users/{target_id}",
                headers=self._auth_headers(admin_token),
                json={"action": "unban"},
            )
        )
        self.assertEqual(unbanned["user_status"], "active")


if __name__ == "__main__":
    unittest.main()
