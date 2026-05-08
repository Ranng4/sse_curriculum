from __future__ import annotations

from app.core.enums import RiskLevel
from app.core.errors import ValidationError
from app.models.user import SuitabilityAssessment
from app.schemas.suitability import RiskQuestion, RiskQuestionOption, RiskQuestionnaireView


class SuitabilityService:
    def __init__(self) -> None:
        self._questionnaire = RiskQuestionnaireView(
            title="投资者适当性风险问卷",
            questions=[
                RiskQuestion(
                    question_id="q1",
                    title="您的投资经验年限是？",
                    options=[
                        RiskQuestionOption(option_key="A", title="不足1年", score=1),
                        RiskQuestionOption(option_key="B", title="1-3年", score=2),
                        RiskQuestionOption(option_key="C", title="3-5年", score=3),
                        RiskQuestionOption(option_key="D", title="5年以上", score=4),
                    ],
                ),
                RiskQuestion(
                    question_id="q2",
                    title="可承受的单次最大亏损比例是？",
                    options=[
                        RiskQuestionOption(option_key="A", title="5%以内", score=1),
                        RiskQuestionOption(option_key="B", title="5%-10%", score=2),
                        RiskQuestionOption(option_key="C", title="10%-20%", score=3),
                        RiskQuestionOption(option_key="D", title="20%以上", score=4),
                    ],
                ),
                RiskQuestion(
                    question_id="q3",
                    title="您的主要投资目标是？",
                    options=[
                        RiskQuestionOption(option_key="A", title="保值", score=1),
                        RiskQuestionOption(option_key="B", title="稳健增值", score=2),
                        RiskQuestionOption(option_key="C", title="成长增值", score=3),
                        RiskQuestionOption(option_key="D", title="高收益", score=4),
                    ],
                ),
            ],
        )
        self._score_bounds: list[tuple[range, RiskLevel]] = [
            (range(0, 5), RiskLevel.C1),
            (range(5, 8), RiskLevel.C2),
            (range(8, 10), RiskLevel.C3),
            (range(10, 12), RiskLevel.C4),
            (range(12, 100), RiskLevel.C5),
        ]

    def get_questionnaire(self) -> RiskQuestionnaireView:
        return self._questionnaire

    def evaluate(self, answers: dict[str, int]) -> SuitabilityAssessment:
        expected_ids = {q.question_id for q in self._questionnaire.questions}
        received_ids = set(answers.keys())
        missing = expected_ids - received_ids
        if missing:
            raise ValidationError(f"missing answers: {sorted(missing)}")

        for key, value in answers.items():
            if value < 0:
                raise ValidationError(f"invalid score for {key}")

        score = sum(answers.values())
        risk_level = self._score_to_risk(score)
        return SuitabilityAssessment(
            completed=True,
            risk_level=risk_level,
            score=score,
            answers=answers,
            submitted_at=None,
        )

    def _score_to_risk(self, score: int) -> RiskLevel:
        for score_range, risk in self._score_bounds:
            if score in score_range:
                return risk
        return RiskLevel.C5
