from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Badge, ChallengeAttempt, User, UserBadge, UserXPTransaction
from app.services.game_service import calculate_level

router = APIRouter(prefix="/api", tags=["progress"])


@router.get("/progress")
def get_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_xp = current_user.xp
    missions_completed = db.query(ChallengeAttempt).filter(ChallengeAttempt.user_id == current_user.id).count()
    accuracy = max(0, min(100, int((missions_completed or 1) * 18)))
    badge_count = db.query(UserBadge).filter(UserBadge.user_id == current_user.id).count()
    streak = 3 if missions_completed > 0 else 0
    return {
        "user": {"id": current_user.id, "username": current_user.username, "role": current_user.role},
        "total_xp": total_xp,
        "level": calculate_level(total_xp),
        "missions_completed": missions_completed,
        "accuracy_rate": accuracy,
        "streak": streak,
        "badges_count": badge_count,
    }


@router.get("/progress/skills")
def get_skill_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [
        {"skill": "Phishing Detection", "mastery": 78},
        {"skill": "Password Security", "mastery": 65},
        {"skill": "Social Engineering", "mastery": 83},
        {"skill": "Incident Response", "mastery": 61},
    ]


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).order_by(User.xp.desc(), User.level.desc()).limit(10).all()
    leaderboard = [
        {"username": user.username, "full_name": user.full_name, "xp": user.xp, "level": user.level, "role": user.role}
        for user in users
    ]
    return leaderboard


@router.get("/badges")
def get_badges(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    awarded_badges = db.query(Badge).join(UserBadge, Badge.id == UserBadge.badge_id).filter(UserBadge.user_id == current_user.id).all()
    all_badges = db.query(Badge).all()
    return {"earned": [badge.name for badge in awarded_badges], "available": [badge.name for badge in all_badges]}
