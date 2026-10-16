from __future__ import annotations

from typing import Any, Dict, List


def evaluate_password_strength(password: str) -> Dict[str, Any]:
    if not password or len(password) < 8:
        return {
            "score": 15,
            "label": "Weak",
            "issues": ["Use at least 12 characters."],
            "suggestions": ["Add a mix of uppercase, lowercase, numbers, and symbols."],
        }

    checks = {
        "length": len(password) >= 12,
        "lowercase": any(ch.islower() for ch in password),
        "uppercase": any(ch.isupper() for ch in password),
        "number": any(ch.isdigit() for ch in password),
        "symbol": any(not ch.isalnum() for ch in password),
    }

    score = sum(20 for value in checks.values() if value)
    if score < 60:
        label = "Weak"
    elif score < 80:
        label = "Moderate"
    else:
        label = "Strong"

    issues = []
    if not checks["length"]:
        issues.append("Password is too short.")
    if not checks["lowercase"]:
        issues.append("Add lowercase letters.")
    if not checks["uppercase"]:
        issues.append("Add uppercase letters.")
    if not checks["number"]:
        issues.append("Add numbers.")
    if not checks["symbol"]:
        issues.append("Add a special character.")

    suggestions = [
        "Avoid common words or names.",
        "Use a unique password for each account.",
        "Consider a passphrase with unrelated words.",
    ]

    return {"score": score, "label": label, "issues": issues, "suggestions": suggestions}


def calculate_level(xp: int) -> int:
    thresholds = [0, 150, 400, 800, 1300, 2000]
    level = 1
    for threshold in thresholds[1:]:
        if xp >= threshold:
            level += 1
    return level


def evaluate_mission_decision(challenge: Dict[str, Any], selected_action: str, reasoning: str, suspicious_indicators: List[str]) -> Dict[str, Any]:
    category = challenge.get("category", "").lower()
    indicators = set(suspicious_indicators)
    correct_actions = {
        "phishing": {"report", "ignore", "flag", "block"},
        "social_engineering": {"verify", "report", "refuse", "escalate"},
        "incident_response": {"report", "contain", "isolate", "escalate"},
    }

    risk_score = 0
    if category == "phishing":
        risk_score = 90 if {"urgent", "spoofed domain", "payment request", "suspicious attachment"}.intersection(indicators) else 60
    elif category == "social engineering":
        risk_score = 85 if {"urgency", "authority pressure", "sensitive data request"}.intersection(indicators) else 55
    elif category == "incident response":
        risk_score = 95 if {"file activity", "alert", "evidence preservation"}.intersection(indicators) else 65

    safe_action = selected_action.lower() in correct_actions.get(category, {"report", "verify", "ignore"})
    score = 100 if safe_action else 40
    if score > 60 and reasoning.strip():
        score += 10
    if not suspicious_indicators:
        score -= 10

    feedback = "You identified the core risk indicators and chose a safe response."
    if not safe_action:
        feedback = "The decision was risky. Consider verifying the sender, checking the source, and reporting the issue instead of engaging."

    xp = max(20, min(120, score // 2))
    return {
        "score": max(0, min(100, score)),
        "xp": xp,
        "safe_action": safe_action,
        "feedback": feedback,
    }
