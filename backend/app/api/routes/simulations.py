from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import AssessmentResult, Challenge, ChallengeAttempt, SimulationMessage, SimulationSession, User, UserXPTransaction
from app.schemas import MissionDecision, SimulationCreate, SimulationMessageIn
from app.services.ai_service import safe_ai_output
from app.services.game_service import calculate_level, evaluate_mission_decision

router = APIRouter(prefix="/api", tags=["simulations"])


@router.post("/simulations")
def create_simulation(payload: SimulationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    challenge = db.query(Challenge).filter(Challenge.id == payload.challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    simulation = SimulationSession(
        user_id=current_user.id,
        challenge_id=challenge.id,
        persona_name=payload.persona_name,
        state_json={"phase": "intro", "progress": 15, "risk_level": "medium"},
        created_at=datetime.utcnow(),
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    ai_message = safe_ai_output(payload.persona_name, challenge.to_dict() if hasattr(challenge, 'to_dict') else challenge.__dict__, "", simulation.state_json)
    db.add(SimulationMessage(session_id=simulation.id, sender="ai", content=ai_message["message"], created_at=datetime.utcnow()))
    db.commit()

    return {"id": simulation.id, "persona_name": payload.persona_name, "message": ai_message["message"], "challenge": challenge.title}


@router.post("/simulations/{simulation_id}/message")
def add_simulation_message(simulation_id: int, payload: SimulationMessageIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = db.query(SimulationSession).filter(SimulationSession.id == simulation_id, SimulationSession.user_id == current_user.id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    ai_response = safe_ai_output(sim.persona_name, {}, payload.content, sim.state_json)
    db.add(SimulationMessage(session_id=simulation_id, sender="user", content=payload.content, created_at=datetime.utcnow()))
    db.add(SimulationMessage(session_id=simulation_id, sender="ai", content=ai_response["message"], created_at=datetime.utcnow()))
    db.commit()
    return {"status": "message received", "ai_response": ai_response}


@router.post("/simulations/{simulation_id}/decision")
def submit_decision(simulation_id: int, payload: MissionDecision, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = db.query(SimulationSession).filter(SimulationSession.id == simulation_id, SimulationSession.user_id == current_user.id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    challenge = db.query(Challenge).filter(Challenge.id == sim.challenge_id).first()
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")

    result = evaluate_mission_decision(
        challenge=challenge.__dict__,
        selected_action=payload.selected_action,
        reasoning=payload.reasoning,
        suspicious_indicators=payload.suspicious_indicators,
    )

    sim.score = result["score"]
    sim.xp_earned = result["xp"]
    sim.state_json = {"phase": "decision", "progress": 80, "risk_level": "high" if result["score"] < 70 else "low"}
    db.commit()

    current_user.xp += result["xp"]
    current_user.level = calculate_level(current_user.xp)
    db.add(UserXPTransaction(user_id=current_user.id, amount=result["xp"], reason="simulation_decision"))
    db.commit()

    return {"score": result["score"], "xp": result["xp"], "feedback": result["feedback"], "safe_action": result["safe_action"]}


@router.post("/simulations/{simulation_id}/complete")
def complete_simulation(simulation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = db.query(SimulationSession).filter(SimulationSession.id == simulation_id, SimulationSession.user_id == current_user.id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim.status = "completed"
    sim.completed_at = datetime.utcnow()
    sim.state_json = {"phase": "complete", "progress": 100, "risk_level": "resolved"}

    attempt = ChallengeAttempt(
        user_id=current_user.id,
        challenge_id=sim.challenge_id,
        status="completed",
        score=sim.score,
        xp_earned=sim.xp_earned,
        attempts_count=1,
        submitted_answer={"simulation_id": sim.id},
    )
    db.add(attempt)
    db.add(AssessmentResult(
        user_id=current_user.id,
        challenge_id=sim.challenge_id,
        score=sim.score,
        accuracy=max(0, min(100, sim.score)),
        summary="Training scenario completed with safe response recommendations.",
    ))
    db.commit()
    return {"status": "completed", "score": sim.score, "xp": sim.xp_earned}
