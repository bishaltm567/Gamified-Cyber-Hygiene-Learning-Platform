from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    xp: int
    level: int
    skill_level: str

    model_config = {"from_attributes": True}


class LearningPathOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    difficulty: str

    model_config = {"from_attributes": True}


class ChallengeOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    difficulty: str
    learning_objectives: List[str]
    scenario_content: Dict[str, Any]
    allowed_actions: List[str]
    evaluation_rubric: Dict[str, Any]
    max_score: int
    xp_reward: int
    explanation: str
    completion_criteria: str
    path_id: Optional[int] = None
    is_published: bool = True

    model_config = {"from_attributes": True}


class MissionDecision(BaseModel):
    selected_action: str
    reasoning: str = ""
    suspicious_indicators: List[str] = []


class SimulationCreate(BaseModel):
    challenge_id: int
    persona_name: str = "Security Coach"


class SimulationMessageIn(BaseModel):
    content: str


class XMLOrJSONResponse(BaseModel):
    pass


class ProgressSummary(BaseModel):
    total_xp: int
    level: int
    next_level_xp: int
    missions_completed: int
    accuracy_rate: int
    streak: int
    badges_count: int


class LeaderboardEntry(BaseModel):
    username: str
    full_name: str
    xp: int
    level: int
    role: str


class AdminChallengeCreate(BaseModel):
    title: str
    description: str
    category: str
    difficulty: str
    learning_objectives: List[str] = []
    scenario_content: Dict[str, Any] = {}
    allowed_actions: List[str] = []
    evaluation_rubric: Dict[str, Any] = {}
    max_score: int = 100
    xp_reward: int = 50
    explanation: str = ""
    completion_criteria: str = ""


class ChallengeAttemptCreate(BaseModel):
    challenge_id: int
    score: int
    xp_earned: int
    status: str = "completed"
    submitted_answer: Dict[str, Any] = {}
