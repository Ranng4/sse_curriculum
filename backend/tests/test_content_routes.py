from __future__ import annotations

import unittest
from uuid import uuid4

from app.main import create_app


class ContentRoutesTestCase(unittest.TestCase):
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

    def _first_market_board_id(self) -> str:
        market = self._assert_ok(self.client.get("/api/v1/forum/markets"))
        return market["boards"][0]["id"]

    def test_post_comment_like_favorite_flow(self):
        user_a_id, user_a_token = self._register_user("Alice")
        user_b_id, user_b_token = self._register_user("Bob")
        board_id = self._first_market_board_id()

        created = self._assert_ok(
            self.client.post(
                "/api/v1/content/posts",
                headers=self._auth_headers(user_a_token),
                json={
                    "board_id": board_id,
                    "title": "贵州茅台估值讨论",
                    "content": "从现金流和ROE看长期配置价值。",
                    "post_type": "longform",
                    "stock_codes": ["600519"],
                },
            ),
            expected_status=201,
        )
        post_id = created["id"]
        self.assertEqual(created["author"]["user_id"], user_a_id)

        comments = self._assert_ok(
            self.client.post(
                f"/api/v1/content/posts/{post_id}/comments",
                headers=self._auth_headers(user_b_token),
                json={"content": "同意，补充下行业周期风险。"},
            ),
            expected_status=201,
        )
        self.assertEqual(comments["author"]["user_id"], user_b_id)

        self._assert_ok(
            self.client.post(
                f"/api/v1/content/posts/{post_id}/like",
                headers=self._auth_headers(user_b_token),
            )
        )
        self._assert_ok(
            self.client.post(
                f"/api/v1/content/posts/{post_id}/favorite",
                headers=self._auth_headers(user_b_token),
            )
        )

        detail = self._assert_ok(
            self.client.get(
                f"/api/v1/content/posts/{post_id}",
                headers=self._auth_headers(user_b_token),
            )
        )
        self.assertTrue(detail["liked_by_me"])
        self.assertTrue(detail["favorited_by_me"])
        self.assertEqual(detail["metrics"]["like_count"], 1)
        self.assertEqual(detail["metrics"]["favorite_count"], 1)
        self.assertEqual(detail["metrics"]["comment_count"], 1)

        comment_list = self._assert_ok(self.client.get(f"/api/v1/content/posts/{post_id}/comments"))
        self.assertEqual(len(comment_list), 1)

        self._assert_ok(
            self.client.delete(
                f"/api/v1/content/posts/{post_id}/like",
                headers=self._auth_headers(user_b_token),
            )
        )
        self._assert_ok(
            self.client.delete(
                f"/api/v1/content/posts/{post_id}/favorite",
                headers=self._auth_headers(user_b_token),
            )
        )
        after = self._assert_ok(
            self.client.get(
                f"/api/v1/content/posts/{post_id}",
                headers=self._auth_headers(user_b_token),
            )
        )
        self.assertFalse(after["liked_by_me"])
        self.assertFalse(after["favorited_by_me"])
        self.assertEqual(after["metrics"]["like_count"], 0)
        self.assertEqual(after["metrics"]["favorite_count"], 0)

    def test_feed_hot_rank_and_search(self):
        user_a_id, user_a_token = self._register_user("Carol")
        _, user_b_token = self._register_user("Dave")
        board_id = self._first_market_board_id()

        post_1 = self._assert_ok(
            self.client.post(
                "/api/v1/content/posts",
                headers=self._auth_headers(user_a_token),
                json={
                    "board_id": board_id,
                    "title": "新能源ETF周观察",
                    "content": "关注成交量与资金净流入变化。",
                    "stock_codes": ["159915"],
                },
            ),
            expected_status=201,
        )
        post_2 = self._assert_ok(
            self.client.post(
                "/api/v1/content/posts",
                headers=self._auth_headers(user_a_token),
                json={
                    "board_id": board_id,
                    "title": "美股科技龙头回调",
                    "content": "短期回撤不改长期成长逻辑。",
                    "stock_codes": ["AAPL"],
                    "post_type": "realtime",
                },
            ),
            expected_status=201,
        )

        self._assert_ok(
            self.client.post(
                f"/api/v1/social/follows/{user_a_id}",
                headers=self._auth_headers(user_b_token),
            )
        )

        feed = self._assert_ok(
            self.client.get(
                "/api/v1/content/feed?following_only=true",
                headers=self._auth_headers(user_b_token),
            )
        )
        post_ids = {item["id"] for item in feed}
        self.assertIn(post_1["id"], post_ids)
        self.assertIn(post_2["id"], post_ids)

        self._assert_ok(
            self.client.post(
                f"/api/v1/content/posts/{post_1['id']}/like",
                headers=self._auth_headers(user_b_token),
            )
        )

        hot_rank = self._assert_ok(self.client.get("/api/v1/content/hot-rank?limit=5"))
        self.assertGreaterEqual(len(hot_rank), 1)

        search = self._assert_ok(self.client.get("/api/v1/content/posts?keyword=新能源&limit=5"))
        self.assertTrue(any(item["id"] == post_1["id"] for item in search))

        suggest = self._assert_ok(self.client.get("/api/v1/content/search/suggest?q=159"))
        self.assertIn("159915", suggest["suggestions"])


if __name__ == "__main__":
    unittest.main()
