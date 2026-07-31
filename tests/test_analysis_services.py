from app.services.analysis_cache_service import AnalysisCacheService
from app.services.analysis_response_service import AnalysisResponseService


def test_cache_key_is_order_independent():
    files = [{"path": "b.py", "content": "b"}, {"path": "a.py", "content": "a"}]
    assert AnalysisCacheService.key("workspace", files) == AnalysisCacheService.key("workspace", list(reversed(files)))


def test_client_response_normalizes_finding():
    response = AnalysisResponseService().to_client_response({
        "risk_score": 71,
        "severity": "High",
        "decision": "BLOCK_DEPLOYMENT",
        "findings": [{"rule": "NO_SECRET", "severity": "High", "file_path": "app.py", "line": 4, "description": "Secret detected"}],
        "ai_analysis": {"confidence": 0.9},
    })
    assert response["riskScore"] == 71
    assert response["summary"]["high"] == 1
    assert response["findings"][0]["lineNumber"] == 4
