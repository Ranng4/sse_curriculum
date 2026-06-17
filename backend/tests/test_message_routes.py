"""Message API route tests — send, conversations, unread count.

AI-generated: unit tests for private messaging endpoints.
"""

from __future__ import annotations

import unittest
from uuid import uuid4

from app.main import create_app


class MessageRoutesTestCase(unittest.TestCase):
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

    def test_send_and_receive_message(self):
        """Full message flow: send, check unread, list conversations, read."""
        user_a_id, token_a = self._register_user("MsgUserA")
        user_b_id, token_b = self._register_user("MsgUserB")

        # A sends message to B
        msg = self._assert_ok(
            self.client.post(
                "/api/v1/messages",
                headers=self._auth_headers(token_a),
                json={
                    "to_user_id": user_b_id,
                    "content": "Hello from A to B!",
                },
            ),
            expected_status=201,
        )
        self.assertEqual(msg["from_id"], user_a_id)
        self.assertEqual(msg["to_id"], user_b_id)

        # B has unread count = 1
        unread = self._assert_ok(
            self.client.get(
                "/api/v1/messages/unread-count",
                headers=self._auth_headers(token_b),
            )
        )
        self.assertEqual(unread["unread_count"], 1)

        # A's conversations show the partner
        convos_a = self._assert_ok(
            self.client.get(
                "/api/v1/messages/conversations",
                headers=self._auth_headers(token_a),
            )
        )
        self.assertEqual(len(convos_a), 1)
        self.assertEqual(convos_a[0]["partner_id"], user_b_id)
        self.assertTrue(convos_a[0]["last_from_me"])

        # B reads the conversation (auto marks read)
        msgs = self._assert_ok(
            self.client.get(
                f"/api/v1/messages/conversations/{user_a_id}",
                headers=self._auth_headers(token_b),
            )
        )
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["content"], "Hello from A to B!")

        # B's unread count should now be 0
        unread_after = self._assert_ok(
            self.client.get(
                "/api/v1/messages/unread-count",
                headers=self._auth_headers(token_b),
            )
        )
        self.assertEqual(unread_after["unread_count"], 0)

    def test_cannot_message_self(self):
        """Sending message to self should fail with 400."""
        uid, token = self._register_user("MsgSelf")
        resp = self.client.post(
            "/api/v1/messages",
            headers=self._auth_headers(token),
            json={"to_user_id": uid, "content": "Self message"},
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("yourself", resp.get_json()["message"])

    def test_empty_conversations(self):
        """New user should have zero conversations."""
        uid, token = self._register_user("MsgEmpty")
        convos = self._assert_ok(
            self.client.get(
                "/api/v1/messages/conversations",
                headers=self._auth_headers(token),
            )
        )
        self.assertEqual(len(convos), 0)


if __name__ == "__main__":
    unittest.main()
