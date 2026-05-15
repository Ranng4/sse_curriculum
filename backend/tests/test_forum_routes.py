from __future__ import annotations

import unittest

from app.main import create_app


class ForumRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_app().test_client()

    def _assert_ok(self, response):
        self.assertIn(response.status_code, (200, 201))
        payload = response.get_json()
        self.assertEqual(payload["code"], 0)
        return payload["data"]

    def test_forum_sections_and_board_crud(self):
        sections = self._assert_ok(self.client.get("/api/v1/forum/sections"))
        self.assertEqual(len(sections), 4)

        market_section = self._assert_ok(self.client.get("/api/v1/forum/markets"))
        self.assertEqual(market_section["category"], "market")
        self.assertTrue(any(item["name"] == "A股" for item in market_section["boards"]))

        created = self._assert_ok(
            self.client.post(
                "/api/v1/forum/boards",
                json={
                    "slug": "test-board",
                    "name": "测试板块",
                    "description": "用于接口测试",
                    "category": "topic",
                    "sort_order": 999,
                },
            )
        )
        board_id = created["id"]
        self.assertEqual(created["name"], "测试板块")

        updated = self._assert_ok(
            self.client.patch(
                f"/api/v1/forum/boards/{board_id}",
                json={"name": "测试板块2", "is_active": False},
            )
        )
        self.assertEqual(updated["name"], "测试板块2")
        self.assertFalse(updated["is_active"])

        delete_payload = self._assert_ok(self.client.delete(f"/api/v1/forum/boards/{board_id}"))
        self.assertIsNone(delete_payload)


if __name__ == "__main__":
    unittest.main()
