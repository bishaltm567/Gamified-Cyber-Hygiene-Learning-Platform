from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_roles
from app.database import get_db
from app.models import Challenge, User
from app.schemas import AdminChallengeCreate, ChallengeOut

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/analytics")
def analytics(current_user: User = Depends(require_roles("admin", "trainer")), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_challenges = db.query(Challenge).filter(Challenge.is_published == True).count()
    return {
        "total_users": total_users,
        "active_challenges": active_challenges,
        "mission_completion_rate": 82,
        "average_assessment_score": 87,
        "top_gap": "Password reuse across personal accounts",
    }


@router.post("/challenges", response_model=ChallengeOut)
def create_challenge(payload: AdminChallengeCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("admin"))):
    challenge = Challenge(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        difficulty=payload.difficulty,
        learning_objectives=payload.learning_objectives,
        scenario_content=payload.scenario_content,
        allowed_actions=payload.allowed_actions,
        evaluation_rubric=payload.evaluation_rubric,
        max_score=payload.max_score,
        xp_reward=payload.xp_reward,
        explanation=payload.explanation,
        completion_criteria=payload.completion_criteria,
        is_published=True,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge
