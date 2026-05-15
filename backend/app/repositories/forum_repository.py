from __future__ import annotations

from copy import deepcopy

from app.core.errors import ConflictError, NotFoundError
from app.models.forum import ForumBoard, ForumBoardCategory


class InMemoryForumBoardRepository:
    def __init__(self) -> None:
        self._boards: dict[str, ForumBoard] = {}
        self._slug_index: dict[str, str] = {}
        self._seed_defaults()

    def list(self) -> list[ForumBoard]:
        return [deepcopy(board) for board in self._boards.values()]

    def get(self, board_id: str) -> ForumBoard:
        board = self._boards.get(board_id)
        if board is None:
            raise NotFoundError("forum board not found")
        return deepcopy(board)

    def find_by_slug(self, slug: str) -> ForumBoard | None:
        board_id = self._slug_index.get(slug)
        return self.get(board_id) if board_id else None

    def create(self, board: ForumBoard) -> ForumBoard:
        self._check_conflict(board)
        self._boards[board.id] = deepcopy(board)
        self._refresh_indexes(board)
        return deepcopy(board)

    def save(self, board: ForumBoard) -> ForumBoard:
        if board.id not in self._boards:
            raise NotFoundError("forum board not found")
        self._check_conflict(board)
        self._boards[board.id] = deepcopy(board)
        self._refresh_indexes(board)
        return deepcopy(board)

    def delete(self, board_id: str) -> None:
        if board_id not in self._boards:
            raise NotFoundError("forum board not found")
        del self._boards[board_id]
        self._slug_index = {slug: saved_id for slug, saved_id in self._slug_index.items() if saved_id != board_id}

    def _check_conflict(self, board: ForumBoard) -> None:
        existing = self._slug_index.get(board.slug)
        if existing and existing != board.id:
            raise ConflictError("forum board slug already exists")

    def _refresh_indexes(self, board: ForumBoard) -> None:
        self._slug_index = {slug: saved_id for slug, saved_id in self._slug_index.items() if saved_id != board.id}
        self._slug_index[board.slug] = board.id

    def _seed_defaults(self) -> None:
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
