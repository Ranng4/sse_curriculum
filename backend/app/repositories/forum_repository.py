from __future__ import annotations

from app.core.errors import ConflictError, NotFoundError
from app.models.forum import ForumBoard, ForumBoardCategory
from app.repositories.sqlite_backend import decode_payload, encode_payload, get_connection


class InMemoryForumBoardRepository:
    """
    Backward-compatible class name; now backed by SQLite persistence.
    """

    def __init__(self) -> None:
        self._seed_defaults()

    def list(self) -> list[ForumBoard]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT payload FROM forum_boards ORDER BY sort_order ASC, created_at ASC"
            ).fetchall()
        return [decode_payload(row["payload"]) for row in rows]

    def get(self, board_id: str) -> ForumBoard:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT payload FROM forum_boards WHERE id = ?",
                (board_id,),
            ).fetchone()
        if row is None:
            raise NotFoundError("forum board not found")
        return decode_payload(row["payload"])

    def find_by_slug(self, slug: str) -> ForumBoard | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT payload FROM forum_boards WHERE slug = ?",
                (slug,),
            ).fetchone()
        if row is None:
            return None
        return decode_payload(row["payload"])

    def create(self, board: ForumBoard) -> ForumBoard:
        self._check_conflict(board)
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO forum_boards
                (id, slug, category, market, sort_order, is_active, created_at, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    board.id,
                    board.slug,
                    board.category.value,
                    board.market,
                    board.sort_order,
                    1 if board.is_active else 0,
                    board.created_at.isoformat(),
                    encode_payload(board),
                ),
            )
            conn.commit()
        return self.get(board.id)

    def save(self, board: ForumBoard) -> ForumBoard:
        self._check_conflict(board)
        with get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE forum_boards
                SET slug = ?, category = ?, market = ?, sort_order = ?, is_active = ?, payload = ?
                WHERE id = ?
                """,
                (
                    board.slug,
                    board.category.value,
                    board.market,
                    board.sort_order,
                    1 if board.is_active else 0,
                    encode_payload(board),
                    board.id,
                ),
            )
            conn.commit()
        if cursor.rowcount == 0:
            raise NotFoundError("forum board not found")
        return self.get(board.id)

    def delete(self, board_id: str) -> None:
        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM forum_boards WHERE id = ?",
                (board_id,),
            )
            conn.commit()
        if cursor.rowcount == 0:
            raise NotFoundError("forum board not found")

    def _check_conflict(self, board: ForumBoard) -> None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM forum_boards WHERE slug = ?",
                (board.slug,),
            ).fetchone()
        if row and row["id"] != board.id:
            raise ConflictError("forum board slug already exists")

    def _seed_defaults(self) -> None:
        with get_connection() as conn:
            row = conn.execute("SELECT COUNT(1) AS c FROM forum_boards").fetchone()
        if row and row["c"] > 0:
            return

        defaults = [
            ForumBoard(
                slug="a-share",
                name="A股",
                description="A股市场热点、个股和趋势讨论",
                category=ForumBoardCategory.MARKET,
                market="A股",
                sort_order=10,
            ),
            ForumBoard(
                slug="hk-stock",
                name="港股",
                description="港股市场机会、政策与交易讨论",
                category=ForumBoardCategory.MARKET,
                market="港股",
                sort_order=20,
            ),
            ForumBoard(
                slug="us-stock",
                name="美股",
                description="美股公司、指数与海外投资交流",
                category=ForumBoardCategory.MARKET,
                market="美股",
                sort_order=30,
            ),
            ForumBoard(
                slug="future",
                name="期货",
                description="期货策略、品种和风险控制讨论",
                category=ForumBoardCategory.MARKET,
                market="期货",
                sort_order=40,
            ),
            ForumBoard(
                slug="value-investing",
                name="价值投资专区",
                description="长期价值、估值和安全边际讨论",
                category=ForumBoardCategory.TOPIC,
                sort_order=10,
            ),
            ForumBoard(
                slug="quant-investing",
                name="量化投资专区",
                description="因子、模型、回测与交易系统讨论",
                category=ForumBoardCategory.TOPIC,
                sort_order=20,
            ),
            ForumBoard(
                slug="fund-investing",
                name="基金投资专区",
                description="基金配置、定投、指数和组合讨论",
                category=ForumBoardCategory.TOPIC,
                sort_order=30,
            ),
            ForumBoard(
                slug="ipo-bond",
                name="新股 / 新债讨论",
                description="新股申购、新债机会与打新策略讨论",
                category=ForumBoardCategory.TOPIC,
                sort_order=40,
            ),
            ForumBoard(
                slug="macro-strategy",
                name="宏观策略研讨",
                description="宏观周期、政策变化和大类资产策略研讨",
                category=ForumBoardCategory.TOPIC,
                sort_order=50,
            ),
            ForumBoard(
                slug="company-research",
                name="公司研究专区",
                description="按行业和个股做深度研究与观点碰撞",
                category=ForumBoardCategory.COMPANY_RESEARCH,
                sort_order=10,
            ),
            ForumBoard(
                slug="industry-research",
                name="行业研究",
                description="行业趋势、景气度和产业链研究",
                category=ForumBoardCategory.COMPANY_RESEARCH,
                parent_id="company-research",
                sort_order=20,
            ),
            ForumBoard(
                slug="stock-research",
                name="个股研究",
                description="单只股票的财务、估值和交易逻辑深度讨论",
                category=ForumBoardCategory.COMPANY_RESEARCH,
                parent_id="company-research",
                sort_order=30,
            ),
            ForumBoard(
                slug="qa-help",
                name="问答求助区",
                description="新手提问、投资解惑和基础答疑",
                category=ForumBoardCategory.QA,
                sort_order=10,
            ),
            ForumBoard(
                slug="newbie-questions",
                name="新手提问",
                description="入门问题、术语解释和操作指引",
                category=ForumBoardCategory.QA,
                parent_id="qa-help",
                sort_order=20,
            ),
            ForumBoard(
                slug="investment-help",
                name="投资解惑",
                description="投资思路、风控和实战问题求助",
                category=ForumBoardCategory.QA,
                parent_id="qa-help",
                sort_order=30,
            ),
        ]

        for board in defaults:
            self.create(board)
