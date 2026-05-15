from __future__ import annotations

from app.core.errors import ConflictError, ValidationError
from app.models.forum import ForumBoard, ForumBoardCategory
from app.repositories.forum_repository import InMemoryForumBoardRepository
from app.schemas.forum import (
    ForumBoardCreateRequest,
    ForumBoardUpdateRequest,
    ForumBoardView,
    ForumSectionView,
)


class ForumService:
    def __init__(self, board_repository: InMemoryForumBoardRepository) -> None:
        self.board_repository = board_repository

    def list_boards(
        self,
        category: ForumBoardCategory | None = None,
        market: str | None = None,
        active_only: bool | None = None,
    ) -> list[ForumBoardView]:
        boards = self.board_repository.list()
        filtered = [
            board
            for board in boards
            if (category is None or board.category == category)
            and (market is None or board.market == market)
            and (active_only is None or board.is_active == active_only)
        ]
        filtered.sort(key=lambda board: (board.sort_order, board.created_at, board.name))
        return [self._to_view(board) for board in filtered]

    def get_board(self, board_id: str) -> ForumBoardView:
        return self._to_view(self.board_repository.get(board_id))

    def get_section(self, category: ForumBoardCategory) -> ForumSectionView:
        board_views = self.list_boards(category=category)
        meta = {
            ForumBoardCategory.MARKET: ("市场讨论区", "按市场划分的投资讨论板块"),
            ForumBoardCategory.TOPIC: ("主题专区", "围绕投资方法与热点展开的主题讨论"),
            ForumBoardCategory.COMPANY_RESEARCH: ("公司研究专区", "按行业和个股进行深度研究"),
            ForumBoardCategory.QA: ("问答求助区", "新手提问和投资解惑集中区"),
        }
        title, description = meta[category]
        return ForumSectionView(category=category, title=title, description=description, boards=board_views)

    def list_sections(self) -> list[ForumSectionView]:
        return [
            self.get_section(ForumBoardCategory.MARKET),
            self.get_section(ForumBoardCategory.TOPIC),
            self.get_section(ForumBoardCategory.COMPANY_RESEARCH),
            self.get_section(ForumBoardCategory.QA),
        ]

    def create_board(self, request: ForumBoardCreateRequest) -> ForumBoardView:
        self._validate_parent(request.parent_id, request.category)
        board = ForumBoard(
            slug=request.slug,
            name=request.name,
            description=request.description,
            category=request.category,
            market=request.market,
            parent_id=request.parent_id,
            sort_order=request.sort_order,
            is_active=request.is_active,
        )
        created = self.board_repository.create(board)
        return self._to_view(created)

    def update_board(self, board_id: str, request: ForumBoardUpdateRequest) -> ForumBoardView:
        board = self.board_repository.get(board_id)
        effective_category = request.category or board.category
        if request.parent_id is not None:
            self._validate_parent(request.parent_id, effective_category, board_id)
        elif request.category is not None and board.parent_id is not None:
            self._validate_parent(board.parent_id, effective_category, board_id)
        if request.slug is not None:
            board.slug = request.slug
        if request.name is not None:
            board.name = request.name
        if request.description is not None:
            board.description = request.description
        if request.category is not None:
            board.category = request.category
        if request.market is not None:
            board.market = request.market
        if request.parent_id is not None:
            board.parent_id = request.parent_id
        if request.sort_order is not None:
            board.sort_order = request.sort_order
        if request.is_active is not None:
            board.is_active = request.is_active
        board.touch()
        saved = self.board_repository.save(board)
        return self._to_view(saved)

    def delete_board(self, board_id: str) -> None:
        board = self.board_repository.get(board_id)
        children = [item for item in self.board_repository.list() if item.parent_id == board.id]
        if children:
            raise ConflictError("board has child boards, delete them first")
        self.board_repository.delete(board_id)

    def _validate_parent(
        self,
        parent_id: str | None,
        category: ForumBoardCategory,
        current_board_id: str | None = None,
    ) -> None:
        if parent_id is None:
            return
        parent = self.board_repository.get(parent_id)
        if current_board_id is not None and parent.id == current_board_id:
            raise ValidationError("parent board cannot be self")
        if parent.category != category:
            raise ValidationError("parent board category mismatch")

    def _to_view(self, board: ForumBoard) -> ForumBoardView:
        return ForumBoardView(
            id=board.id,
            slug=board.slug,
            name=board.name,
            description=board.description,
            category=board.category,
            market=board.market,
            parent_id=board.parent_id,
            sort_order=board.sort_order,
            is_active=board.is_active,
            created_at=board.created_at,
            updated_at=board.updated_at,
        )
