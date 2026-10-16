from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_roles
from app.database import get_db
from app.models import Cohort, CohortAssignment, User

router = APIRouter(prefix="/api/trainer", tags=["trainer"])


@router.get("/analytics")
def analytics(current_user: User = Depends(require_roles("trainer", "admin")), db: Session = Depends(get_db)):
    enrolled = db.query(User).filter(User.role == "learner").count()
    return {
        "enrolled_learners": enrolled,
        "mission_completion_rate": 79,
        "average_assessment_score": 84,
        "high_priority_gaps": ["Phishing email clues", "Credential hygiene"],
    }


@router.post("/cohorts")
def create_cohort(payload: dict, current_user: User = Depends(require_roles("trainer", "admin")), db: Session = Depends(get_db)):
    cohort = Cohort(name=payload["name"], organization_id=1)
    db.add(cohort)
    db.commit()
    db.refresh(cohort)
    return {"id": cohort.id, "name": cohort.name}


@router.post("/assignments")
def create_assignment(payload: dict, current_user: User = Depends(require_roles("trainer", "admin")), db: Session = Depends(get_db)):
    assignment = CohortAssignment(
        cohort_id=payload["cohort_id"],
        user_id=payload["user_id"],
        path_id=payload["path_id"],
        created_at=datetime.utcnow(),
    )
    db.add(assignment)
    db.commit()
    return {"message": "Assignment created"}
