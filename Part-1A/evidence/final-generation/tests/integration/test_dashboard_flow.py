from app.services.validation_service import validate_source


def test_dashboard_validation_returns_structured_report():
    result = validate_source("demo.log", b"pytest failed\nassertionerror\n")
    assert result["summary_status"] == "FAIL"
    assert len(result["findings"]) >= 1
