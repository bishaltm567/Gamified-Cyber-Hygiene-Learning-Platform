from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(80), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    cohorts = relationship("Cohort", back_populates="organization")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, default="")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(40), nullable=False, default="learner")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    skill_level = Column(String(40), default="beginner")
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    attempts = relationship("ChallengeAttempt", back_populates="user")
    simulations = relationship("SimulationSession", back_populates="user")
    mastery = relationship("SkillMastery", back_populates="user")
    xp_transactions = relationship("UserXPTransaction", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(40), default="beginner")
    created_at = Column(DateTime, default=datetime.utcnow)

    lessons = relationship("Lesson", back_populates="path")
    challenges = relationship("Challenge", back_populates="path")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=False)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)

    path = relationship("LearningPath", back_populates="lessons")


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(80), nullable=False)
    difficulty = Column(String(50), nullable=False)
    learning_objectives = Column(JSON, default=list)
    scenario_content = Column(JSON, default=dict)
    allowed_actions = Column(JSON, default=list)
    evaluation_rubric = Column(JSON, default=dict)
    max_score = Column(Integer, default=100)
    xp_reward = Column(Integer, default=50)
    explanation = Column(Text, default="")
    completion_criteria = Column(Text, default="")
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    path = relationship("LearningPath", back_populates="challenges")
    attempts = relationship("ChallengeAttempt", back_populates="challenge")
    simulations = relationship("SimulationSession", back_populates="challenge")
    assessment_results = relationship("AssessmentResult", back_populates="challenge")


class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    status = Column(String(40), default="started")
    score = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    attempts_count = Column(Integer, default=1)
    submitted_answer = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attempts")
    challenge = relationship("Challenge", back_populates="attempts")


class SimulationSession(Base):
    __tablename__ = "simulation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=True)
    persona_name = Column(String(120), default="Security Coach")
    status = Column(String(40), default="in_progress")
    score = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    state_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="simulations")
    challenge = relationship("Challenge", back_populates="simulations")
    messages = relationship("SimulationMessage", back_populates="session")


class SimulationMessage(Base):
    __tablename__ = "simulation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("simulation_sessions.id"), nullable=False)
    sender = Column(String(40), default="ai")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SimulationSession", back_populates="messages")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    score = Column(Integer, default=0)
    accuracy = Column(Integer, default=0)
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    challenge = relationship("Challenge", back_populates="assessment_results")


class SkillMastery(Base):
    __tablename__ = "skill_mastery"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(80), nullable=False)
    mastery = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mastery")


class UserXPTransaction(Base):
    __tablename__ = "user_xp_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, default=0)
    reason = Column(String(120), default="mission")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="xp_transactions")


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    icon = Column(String(40), default="shield")
    created_at = Column(DateTime, default=datetime.utcnow)


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)


class LearningStreak(Base):
    __tablename__ = "learning_streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Cohort(Base):
    __tablename__ = "cohorts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="cohorts")


class CohortAssignment(Base):
    __tablename__ = "cohort_assignments"

    id = Column(Integer, primary_key=True, index=True)
    cohort_id = Column(Integer, ForeignKey("cohorts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(120), nullable=False)
    details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
