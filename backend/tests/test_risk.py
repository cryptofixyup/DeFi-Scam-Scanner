from app.evm import OnChainObservation, InvalidEVMAddress, normalize_evm_address
from app.risk import score_observation


def observation(tx_count: int = 10) -> OnChainObservation:
    return OnChainObservation("0x" + "1" * 40, "ethereum", 0, tx_count, False, 100)


def test_valid_evm_address_normalizes():
    assert normalize_evm_address(" 0x" + "A" * 40) == "0x" + "a" * 40


def test_invalid_evm_address_rejected():
    try:
        normalize_evm_address("0x123")
    except InvalidEVMAddress:
        return
    raise AssertionError("invalid address accepted")


def test_known_scam_is_critical():
    result = score_observation(observation(), {"severity": 90, "category": "PHISHING", "source": "internal"})
    assert result["score"] == 90
    assert result["risk"] == "CRITICAL"
    assert result["status"] == "KNOWN_SCAM"
    assert result["confidence"] == "HIGH"


def test_unknown_active_wallet_has_no_false_safe_claim():
    result = score_observation(observation(), None)
    assert result["status"] == "NO_KNOWN_FLAGS"
    assert result["confidence"] == "MEDIUM"


def test_new_wallet_is_low_confidence():
    result = score_observation(observation(0), None)
    assert result["confidence"] == "LOW"
    assert result["score"] == 5
