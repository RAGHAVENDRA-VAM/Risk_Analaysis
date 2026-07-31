from app.services.analysis_cache_service import AnalysisCacheService
from app.services.analysis_response_service import AnalysisResponseService
from app.agents import CoordinatorAgent
from app.services.rule_engine_service import RuleEngineService


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


def test_coordinator_returns_all_specialists():
    result = CoordinatorAgent().coordinate([{"category": "Security", "score": 100}])
    assert len(result["specialists"]) == 8


def test_platform_rules_cover_docker_and_bicep():
    engine = RuleEngineService()
    findings = engine.execute([
        {"path": "Dockerfile", "content": "FROM python:latest\nRUN pip install app"},
        {"path": "infra/main.bicep", "content": "resource ip 'Microsoft.Network/publicIPAddresses@2023' = {}"},
    ])["findings"]
    assert {item["rule"] for item in findings} >= {"DOCKER_LATEST_TAG", "DOCKER_ROOT_USER", "CLOUD_PUBLIC_EXPOSURE"}
