from __future__ import annotations

from datetime import UTC, datetime

from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.suitability import SuitabilityResultView
from app.services.suitability_service import SuitabilityService


class UserService:
    def __init__(
        self,
        user_repository: InMemoryUserRepository,
        suitability_service: SuitabilityService,
    ) -> None:
        self.user_repository = user_repository
        self.suitability_service = suitability_service

    def submit_suitability_assessment(
        self,
        user_id: str,
        answers: dict[str, int],
    ) -> SuitabilityResultView:
        user = self.user_repository.get(user_id)

        result = self.suitability_service.evaluate(answers)
        result.submitted_at = datetime.now(UTC)
        user.suitability_assessment = result
        user.touch()
        saved = self.user_repository.save(user)
        return SuitabilityResultView(
            completed=saved.suitability_assessment.completed,
            risk_level=saved.suitability_assessment.risk_level,
            score=saved.suitability_assessment.score,
            answers=saved.suitability_assessment.answers,
            submitted_at=saved.suitability_assessment.submitted_at,
        )

    def get_suitability_result(self, user_id: str) -> SuitabilityResultView:
        user = self.user_repository.get(user_id)
        assessment = user.suitability_assessment
        return SuitabilityResultView(
            completed=assessment.completed,
            risk_level=assessment.risk_level,
            score=assessment.score,
            answers=assessment.answers,
            submitted_at=assessment.submitted_at,
        )
