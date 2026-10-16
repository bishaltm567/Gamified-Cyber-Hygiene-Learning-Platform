from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.routes import admin, auth, learning, progress, simulations, trainer
from app.auth import hash_password
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Badge, Challenge, LearningPath, Lesson, Organization, User, UserBadge

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(learning.router)
app.include_router(simulations.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(trainer.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()


def seed_demo_data(db: Session):
    demo_accounts = {
        "learner@cyberquest.academy": {
            "username": "demolearner",
            "full_name": "Avery Chen",
            "role": "learner",
            "xp": 420,
            "level": 2,
            "skill_level": "intermediate",
        },
        "trainer@cyberquest.academy": {
            "username": "demotrainer",
            "full_name": "Morgan Wells",
            "role": "trainer",
            "xp": 680,
            "level": 3,
            "skill_level": "advanced",
        },
        "admin@cyberquest.academy": {
            "username": "demoadmin",
            "full_name": "Jordan Patel",
            "role": "admin",
            "xp": 950,
            "level": 4,
            "skill_level": "advanced",
        },
    }

    organization = db.query(Organization).filter(Organization.slug == "northwind-security").first()
    if organization is None:
        organization = Organization(name="Northwind Security Academy", slug="northwind-security")
        db.add(organization)
        db.commit()
        db.refresh(organization)
    else:
        db.flush()

    created_users = []
    for email, account in demo_accounts.items():
        user = db.query(User).filter(or_(User.email == email, User.username == account["username"])).first()
        if user is None:
            user = User(
                email=email,
                username=account["username"],
                full_name=account["full_name"],
                password_hash=hash_password("demo123"),
                role=account["role"],
                organization_id=organization.id,
                xp=account["xp"],
                level=account["level"],
                skill_level=account["skill_level"],
                created_at=datetime.utcnow(),
            )
            db.add(user)
            created_users.append(user)
        else:
            user.email = email
            user.username = account["username"]
            user.full_name = account["full_name"]
            user.password_hash = hash_password("demo123")
            user.role = account["role"]
            user.organization_id = organization.id
            user.xp = account["xp"]
            user.level = account["level"]
            user.skill_level = account["skill_level"]
            created_users.append(user)

    db.commit()

    path_specs = [
        {"name": "Cyber Hygiene Fundamentals", "slug": "cyber-hygiene-fundamentals", "description": "Build the core habits behind secure digital behavior.", "difficulty": "beginner"},
        {"name": "Phishing and Email Security", "slug": "phishing-email-security", "description": "Spot fake senders, malicious links, and deceptive urgency.", "difficulty": "beginner"},
        {"name": "Password and Account Security", "slug": "password-account-security", "description": "Protect login credentials and account recovery flows.", "difficulty": "intermediate"},
        {"name": "Social Engineering Awareness", "slug": "social-engineering-awareness", "description": "Recognize pressure, impersonation, and manipulation.", "difficulty": "intermediate"},
        {"name": "Internship and Job Scam Detection", "slug": "internship-job-scam-detection", "description": "Identify fake offers and red flags in recruitment messages.", "difficulty": "intermediate"},
        {"name": "Ransomware Awareness", "slug": "ransomware-awareness", "description": "Learn to identify suspicious indicators and respond safely.", "difficulty": "advanced"},
        {"name": "Insider Threat Awareness", "slug": "insider-threat-awareness", "description": "Understand risky behavior and evidence handling.", "difficulty": "advanced"},
        {"name": "Incident Response Fundamentals", "slug": "incident-response-fundamentals", "description": "Practice response actions, escalation, and safety.", "difficulty": "advanced"},
    ]
    existing_path_slugs = {path.slug for path in db.query(LearningPath).all()}
    paths = []
    for spec in path_specs:
        if spec["slug"] in existing_path_slugs:
            existing_path = db.query(LearningPath).filter(LearningPath.slug == spec["slug"]).first()
            if existing_path is not None:
                paths.append(existing_path)
            continue
        item = LearningPath(**spec)
        db.add(item)
        db.flush()
        paths.append(item)
        lesson_titles = ["Foundations", "Key Threats", "Safe Practice"]
        for title in lesson_titles:
            db.add(Lesson(title=title, content=f"Training content for {spec['name']} — {title}.", path_id=item.id))

    db.commit()

    challenges = [
        {"title": "Phishing Inbox Triage", "description": "Inspect the email and decide whether to report or ignore it.", "category": "phishing", "difficulty": "beginner", "learning_objectives": ["Identify urgency", "Examine the sender domain", "Spot unsafe links"], "scenario_content": {"sender": "finance@northwind.example", "subject": "Immediate action required", "body": "Your payroll access is locked. Click immediately to verify your account before midnight.", "action": "verify"}, "allowed_actions": ["report", "ignore", "safe verify"], "evaluation_rubric": {"correct": ["report", "ignore"], "max_score": 100}, "max_score": 100, "xp_reward": 60, "explanation": "Urgent requests, mismatched domains, and pressure to act quickly are classic phishing signals.", "completion_criteria": "Select a safe action and identify at least three indicators.", "path_name": "Phishing and Email Security"},
        {"title": "Password Guardian Check", "description": "Use the sample password checker to assess a fictional password.", "category": "password_security", "difficulty": "beginner", "learning_objectives": ["Estimate strength", "Spot common patterns", "Improve password quality"], "scenario_content": {"sample_password": "Winter2024!"}, "allowed_actions": ["check strength", "suggest improvements"], "evaluation_rubric": {"correct": ["length", "symbols", "case variation"], "max_score": 100}, "max_score": 100, "xp_reward": 55, "explanation": "Longer passwords with varied character types are more resilient against guessing.", "completion_criteria": "Assess the sample password and identify at least two improvements.", "path_name": "Password and Account Security"},
        {"title": "Recruiter Offer Review", "description": "Review an internship message and decide whether it is legitimate or likely fake.", "category": "social_engineering", "difficulty": "intermediate", "learning_objectives": ["Check recruiter identity", "Detect unrealistic pay", "Avoid sending personal information"], "scenario_content": {"offer": "We have selected you for an internship requiring a payment deposit to get started."}, "allowed_actions": ["verify company", "report", "do not send documents"], "evaluation_rubric": {"correct": ["verify", "report"], "max_score": 100}, "max_score": 100, "xp_reward": 75, "explanation": "Legitimate employers do not ask applicants to pay a fee or send personal details before verifying identity.", "completion_criteria": "Flag the fake offer and explain the risks.", "path_name": "Internship and Job Scam Detection"},
        {"title": "Secure Login Response", "description": "A suspicious IT caller asks for a verification code. Decide how to respond.", "category": "social_engineering", "difficulty": "intermediate", "learning_objectives": ["Resist authority pressure", "Avoid sharing authentication codes", "Use escalation paths"], "scenario_content": {"caller": "This is the IT desk. We need your code to reset your account immediately."}, "allowed_actions": ["verify through official channel", "refuse to share", "escalate"], "evaluation_rubric": {"correct": ["verify through official channel", "refuse"], "max_score": 100}, "max_score": 100, "xp_reward": 80, "explanation": "No legitimate support team should ask for a passcode over an unsolicited call.", "completion_criteria": "Reject the request and use a trusted verification channel.", "path_name": "Social Engineering Awareness"},
        {"title": "Suspicious Attachment Check", "description": "Use the evidence provided to classify the attachment safely.", "category": "phishing", "difficulty": "intermediate", "learning_objectives": ["Inspect attachments", "Look for mismatched details", "Avoid opening unknown files"], "scenario_content": {"attachment": "invoice-final.zip", "sender": "accounts@secure-service.xyz"}, "allowed_actions": ["delete", "report", "scan in sandbox"], "evaluation_rubric": {"correct": ["delete", "report"], "max_score": 100}, "max_score": 100, "xp_reward": 80, "explanation": "Unexpected archives with mismatched identity clues should be treated as unsafe.", "completion_criteria": "Do not open the attachment and explain the reason.", "path_name": "Phishing and Email Security"},
        {"title": "Ransomware Warning Signs", "description": "Determine the appropriate containment step for the active incident.", "category": "incident_response", "difficulty": "advanced", "learning_objectives": ["Recognize indicators of compromise", "Contain before escalating", "Preserve evidence"], "scenario_content": {"alert": "Several files renamed with a .locked extension and a ransom note appeared."}, "allowed_actions": ["isolate host", "preserve evidence", "contact incident response"], "evaluation_rubric": {"correct": ["isolate", "preserve evidence"], "max_score": 100}, "max_score": 100, "xp_reward": 90, "explanation": "Isolate the device immediately and preserve forensic evidence before recovery actions.", "completion_criteria": "Choose a containment path and document the event.", "path_name": "Ransomware Awareness"},
        {"title": "Insider Risk Review", "description": "Investigate unusual access patterns without accusing the employee prematurely.", "category": "incident_response", "difficulty": "advanced", "learning_objectives": ["Distinguish unusual from malicious", "Use evidence", "Maintain privacy"], "scenario_content": {"log": "An employee downloaded unusually large reports outside normal work hours."}, "allowed_actions": ["review access logs", "escalate to security", "document timeline"], "evaluation_rubric": {"correct": ["review logs", "document timeline"], "max_score": 100}, "max_score": 100, "xp_reward": 90, "explanation": "Evidence-based investigation is safer than unsupported accusations.", "completion_criteria": "Choose an investigation path based on verified facts.", "path_name": "Insider Threat Awareness"},
        {"title": "Incident Ticket Escalation", "description": "A suspicious phishing alert requires the right legal and operational next step.", "category": "incident_response", "difficulty": "advanced", "learning_objectives": ["Escalate properly", "Avoid unnecessary exposure", "Document actions"], "scenario_content": {"ticket": "A user clicked a malicious link and entered their work credentials."}, "allowed_actions": ["reset credentials", "report to security", "monitor account"], "evaluation_rubric": {"correct": ["reset credentials", "report to security"], "max_score": 100}, "max_score": 100, "xp_reward": 95, "explanation": "Fast credential reset and formal escalation reduce the risk of compromise.", "completion_criteria": "Choose the correct safety and reporting sequence.", "path_name": "Incident Response Fundamentals"},
        {"title": "Urgent Bank Verification", "description": "A fake message claims the bank is blocking your account. How do you react?", "category": "phishing", "difficulty": "beginner", "learning_objectives": ["Avoid direct links", "Verify through official channels", "Recognize urgency"], "scenario_content": {"subject": "Action required: account locked", "link": "https://secure-alert-bank-login.example/verify"}, "allowed_actions": ["contact bank directly", "report", "ignore"], "evaluation_rubric": {"correct": ["contact bank directly", "ignore"], "max_score": 100}, "max_score": 100, "xp_reward": 60, "explanation": "Never trust urgent alerts delivered by email alone. Verify through a known official route.", "completion_criteria": "Select a safe verification method and avoid clicking the link.", "path_name": "Phishing and Email Security"},
        {"title": "LinkedIn Message Check", "description": "A recruiter asks for a resume and a copy of your ID immediately.", "category": "social_engineering", "difficulty": "beginner", "learning_objectives": ["Question pressure", "Check employer identity", "Limit information sharing"], "scenario_content": {"profile": "Concierge Ventures", "request": "Send your ID and bank details for onboarding"}, "allowed_actions": ["verify company", "question request", "refuse to share"], "evaluation_rubric": {"correct": ["verify", "refuse"], "max_score": 100}, "max_score": 100, "xp_reward": 70, "explanation": "Requesting personal or financial information before a verified hiring process is a major red flag.", "completion_criteria": "Do not share sensitive documents without confirmed identity.", "path_name": "Internship and Job Scam Detection"},
        {"title": "Blue Team Response Drill", "description": "A user reports a strange warning banner. Decide the response chain.", "category": "incident_response", "difficulty": "intermediate", "learning_objectives": ["Escalate quickly", "Use an approved incident flow", "Protect the user"], "scenario_content": {"warning": "Suspicious sign-in prompt from unusual device"}, "allowed_actions": ["revoke session", "report to security", "ask user to isolate"], "evaluation_rubric": {"correct": ["report", "revoke session"], "max_score": 100}, "max_score": 100, "xp_reward": 85, "explanation": "Quick account containment and reporting reduce damage while preserving user trust.", "completion_criteria": "Select the right response and explain why.", "path_name": "Incident Response Fundamentals"},
        {"title": "Password Reuse Warning", "description": "Review whether a reused password should be replaced.", "category": "password_security", "difficulty": "intermediate", "learning_objectives": ["Identify password reuse", "Recommend safe password managers", "Promote unique credentials"], "scenario_content": {"password": "football123"}, "allowed_actions": ["change password", "use a password manager", "avoid reuse"], "evaluation_rubric": {"correct": ["change password", "use manager"], "max_score": 100}, "max_score": 100, "xp_reward": 65, "explanation": "Reusing passwords across systems creates a chain reaction if one account is breached.", "completion_criteria": "Recommend unique, stored credentials instead of reuse.", "path_name": "Password and Account Security"},
        {"title": "Fake Vendor Call", "description": "Someone impersonates a supplier and asks for purchase details.", "category": "social_engineering", "difficulty": "advanced", "learning_objectives": ["Verify vendor identity", "Use standard workflow", "Escalate unusual requests"], "scenario_content": {"vendor": "Acme Supplies", "request": "Send the purchase approval code by email right now."}, "allowed_actions": ["verify vendor through known contact", "refuse code", "escalate"], "evaluation_rubric": {"correct": ["verify", "refuse"], "max_score": 100}, "max_score": 100, "xp_reward": 90, "explanation": "Requests for approval codes or payment details should never be fulfilled without identity verification.", "completion_criteria": "Refuse and validate the vendor through an official channel.", "path_name": "Social Engineering Awareness"},
        {"title": "Suspicious Data Download", "description": "A user downloads a file from an untrusted person. What should happen next?", "category": "incident_response", "difficulty": "advanced", "learning_objectives": ["Protect the endpoint", "Review the file origin", "Contact the right teams"], "scenario_content": {"download": "employee-transfer-list.xlsx"}, "allowed_actions": ["scan the file", "isolate machine", "report to security"], "evaluation_rubric": {"correct": ["isolate", "report to security"], "max_score": 100}, "max_score": 100, "xp_reward": 95, "explanation": "A suspicious download should be treated as a possible malware or data exfiltration event until checked.", "completion_criteria": "Choose an isolation and reporting strategy.", "path_name": "Ransomware Awareness"},
        {"title": "Credential Hygiene Quiz", "description": "Review a checklist for keeping credentials secure across systems.", "category": "password_security", "difficulty": "beginner", "learning_objectives": ["Use MFA", "Avoid reuse", "Watch for password sprays"], "scenario_content": {"checklist": ["use MFA", "unique passwords", "recovery email verification"]}, "allowed_actions": ["enable MFA", "use unique passwords", "review recovery methods"], "evaluation_rubric": {"correct": ["MFA", "unique passwords"], "max_score": 100}, "max_score": 100, "xp_reward": 50, "explanation": "Strong account hygiene means MFA, unique credentials, and regular recovery reviews.", "completion_criteria": "Select the most important safeguards for account security.", "path_name": "Password and Account Security"},
    ]

    path_lookup = {path.name: path.id for path in paths}
    for item in challenges:
        if db.query(Challenge).filter(Challenge.title == item["title"]).first():
            continue
        challenge = Challenge(
            title=item["title"],
            description=item["description"],
            category=item["category"],
            difficulty=item["difficulty"],
            learning_objectives=item["learning_objectives"],
            scenario_content=item["scenario_content"],
            allowed_actions=item["allowed_actions"],
            evaluation_rubric=item["evaluation_rubric"],
            max_score=item["max_score"],
            xp_reward=item["xp_reward"],
            explanation=item["explanation"],
            completion_criteria=item["completion_criteria"],
            path_id=path_lookup.get(item["path_name"]),
            is_published=True,
            created_at=datetime.utcnow(),
        )
        db.add(challenge)

    badge_specs = [
        ("First Mission Complete", "Completed your first cyber hygiene challenge.", "star"),
        ("Phishing Spotter", "Correctly identified phishing indicators.", "shield"),
        ("Password Guardian", "Protected account credentials with safe habits.", "lock"),
        ("Social Engineering Defender", "Resisted manipulation attempts successfully.", "users"),
        ("Incident Response Rookie", "Used correct escalation paths in incident drills.", "alert-circle"),
        ("Five-Day Learning Streak", "Maintained a five-day learning streak.", "flame"),
        ("Cyber Hygiene Champion", "Reached a strong level of mastery across the platform.", "trophy"),
    ]
    existing_badge_names = {badge.name for badge in db.query(Badge).all()}
    for name, description, icon in badge_specs:
        if name in existing_badge_names:
            continue
        db.add(Badge(name=name, description=description, icon=icon))

    db.commit()
    learner = db.query(User).filter(User.email == "learner@cyberquest.academy").first()
    if learner is not None:
        for badge in db.query(Badge).all()[:3]:
            if not db.query(UserBadge).filter(UserBadge.user_id == learner.id, UserBadge.badge_id == badge.id).first():
                db.add(UserBadge(user_id=learner.id, badge_id=badge.id))
        db.commit()

    return {"status": "seeded"}
