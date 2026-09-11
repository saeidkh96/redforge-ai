from redforge.roadmap_v200.hardening import EvidenceIntegrity, ReleaseGateEvaluator


def test_evidence_integrity_and_gate_hash() -> None:
    evidence = {
        "verification_passed": True,
        "review_approved": True,
        "audit_present": True,
        "human_approval_required": False,
        "human_approval_granted": False,
    }
    digest = EvidenceIntegrity.digest(evidence)
    assert EvidenceIntegrity.verify(evidence, digest)
    gate = ReleaseGateEvaluator().evaluate(evidence)
    assert gate.passed
    assert gate.evidence_hash == digest
