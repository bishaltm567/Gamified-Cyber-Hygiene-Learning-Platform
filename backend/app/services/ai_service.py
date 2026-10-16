from __future__ import annotations

from typing import Any, Dict, List, Optional


def validate_response(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    required = ["message", "scenario_state", "available_actions", "risk_indicators", "feedback", "score_delta", "mission_complete"]
    return all(key in payload for key in required)


def mock_ai_response(persona_name: str, challenge: Dict[str, Any], user_message: str = "", scenario_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    category = challenge.get("category", "security")
    risk_indicators = [
        "Urgency and pressure",
        "Unexpected request for credentials",
        "Suspicious sender or domain",
    ]
    if category == "incident_response":
        risk_indicators = ["Unusual file activity", "Repeated security alerts", "Evidence preservation required"]
    elif category == "password_security":
        risk_indicators = ["Short length", "No symbol variation", "Common word pattern"]

    payload = {
        "message": f"{persona_name} is guiding the scenario. The most relevant warning signs are the urgency and missing verification checks.",
        "scenario_state": scenario_state or {"step": 1, "progress": 25, "risk_level": "medium"},
        "available_actions": ["verify source", "ask for evidence", "report suspicious activity", "pause and review"],
        "risk_indicators": risk_indicators,
        "feedback": "You should verify the request, check the sender identity, and avoid sharing sensitive information until the origin is confirmed.",
        "score_delta": 12,
        "mission_complete": False,
    }
    if user_message.lower().find("report") >= 0 or user_message.lower().find("verify") >= 0:
        payload["score_delta"] = 18
    if category == "incident_response":
        payload["available_actions"] = ["isolate device", "preserve evidence", "contact incident response", "document actions"]
    return payload


def safe_ai_output(persona_name: str, challenge: Dict[str, Any], user_message: str = "", scenario_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    output = mock_ai_response(persona_name, challenge, user_message, scenario_state)
    if not validate_response(output):
        fallback = {
            "message": "The simulation is continuing with a safe fallback path.",
            "scenario_state": scenario_state or {"step": 1, "progress": 10, "risk_level": "low"},
            "available_actions": ["review evidence", "ask about verification", "report suspicious activity"],
            "risk_indicators": ["Unexpected pressure", "Missing proof"],
            "feedback": "Take a moment to verify before acting.",
            "score_delta": 5,
            "mission_complete": False,
        }
        return fallback
    return output
