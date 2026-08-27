from .evm import OnChainObservation

ENGINE_VERSION = "1.0.0"


def score_observation(observation: OnChainObservation, scam: dict | None) -> dict:
    evidence: list[dict] = []
    score = 0
    if scam:
        score = max(score, min(100, scam["severity"]))
        evidence.append({"code": "KNOWN_SCAM", "severity": "critical", "message": f"Address is listed as {scam['category']}.", "source": scam["source"]})
    if observation.transaction_count == 0:
        score += 5
        evidence.append({"code": "NO_TRANSACTION_HISTORY", "severity": "low", "message": "No transactions were observed at the latest block.", "source": "on_chain"})
    status = "KNOWN_SCAM" if scam else ("SUSPICIOUS" if score >= 50 else "NO_KNOWN_FLAGS")
    risk = "CRITICAL" if score >= 75 else "HIGH" if score >= 50 else "GUARDED" if score >= 25 else "LOW"
    confidence = "HIGH" if scam else "MEDIUM" if observation.transaction_count > 0 else "LOW"
    return {"score": min(score, 100), "risk": risk, "confidence": confidence, "status": status, "engine_version": ENGINE_VERSION, "evidence": evidence}
