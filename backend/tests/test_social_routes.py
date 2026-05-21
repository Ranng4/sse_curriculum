from __future__ import annotations

import unittest
from uuid import uuid4

from app.main import create_app


class SocialRoutesTestCase(unittest.TestCase):
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
        phone = f"138{suffix}"
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

    def test_follow_unfollow_and_stats(self):
        user_a_id, user_a_token = self._register_user("Echo")
        user_b_id, user_b_token = self._register_user("Foxtrot")

        action = self._assert_ok(
            self.client.post(
                f"/api/v1/social/follows/{user_b_id}",
                headers=self._auth_headers(user_a_token),
            )
        )
        self.assertTrue(action["is_following"])
        self.assertEqual(action["following_count"], 1)

        following = self._assert_ok(
            self.client.get(
                "/api/v1/social/follows/me",
                headers=self._auth_headers(user_a_token),
            )
        )
        self.assertTrue(any(item["user_id"] == user_b_id for item in following))

        followers = self._assert_ok(
            self.client.get(
                "/api/v1/social/fans/me",
                headers=self._auth_headers(user_b_token),
            )
        )
        self.assertTrue(any(item["user_id"] == user_a_id for item in followers))

        stats = self._assert_ok(
            self.client.get(
                "/api/v1/social/stats/me",
                headers=self._auth_headers(user_a_token),
            )
        )
        self.assertEqual(stats["following_count"], 1)

        action = self._assert_ok(
            self.client.delete(
                f"/api/v1/social/follows/{user_b_id}",
                headers=self._auth_headers(user_a_token),
            )
        )
        self.assertFalse(action["is_following"])
        self.assertEqual(action["following_count"], 0)


if __name__ == "__main__":
    unittest.main()
