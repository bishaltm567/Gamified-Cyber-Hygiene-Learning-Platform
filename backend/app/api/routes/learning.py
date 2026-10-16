from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Challenge, LearningPath, Lesson
from app.schemas import ChallengeOut, LearningPathOut

router = APIRouter(prefix="/api", tags=["learning"])


@router.get("/learning-paths", response_model=List[LearningPathOut])
def get_learning_paths(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(LearningPath).order_by(LearningPath.id).all()


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.get("/challenges", response_model=List[ChallengeOut])
def get_challenges(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Challenge).filter(Challenge.is_published == True).order_by(Challenge.id).all()


@router.get("/challenges/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge
