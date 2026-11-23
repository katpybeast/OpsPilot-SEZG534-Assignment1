from app.rules.rule_registry import get_active_rule_ids
from app.rules.security_rules import evaluate_security_rules
from app.services.validation_service import validate_source


def test_security_privileged_container_detected():
    sample = "securityContext:\n  privileged: true"
    findings = evaluate_security_rules(sample)
    assert any(item.rule_id == "security_privileged_container" for item in findings)


def test_security_missing_limits_detected():
    sample = "image: nginx"
    findings = evaluate_security_rules(sample)
    assert any(item.rule_id == "security_missing_resource_limits" for item in findings)


def test_security_rule_coverage_documented():
    total_rules = len(get_active_rule_ids())
    covered = {
        "ci_cd_dependency_failure",
        "ci_cd_test_failure",
        "ci_cd_build_failure",
        "docker_root_user",
        "docker_exposed_port_22",
        "docker_missing_security_user",
        "k8s_invalid_yaml",
        "k8s_missing_resource_limits",
        "k8s_privileged_container",
        "security_privileged_container",
        "security_missing_resource_limits",
    }
    coverage = len(covered & set(get_active_rule_ids())) / total_rules
    assert coverage >= 0.9


def test_security_findings_are_deduplicated_in_final_report():
    sample = (
        "apiVersion: v1\n"
        "kind: Pod\n"
        "metadata:\n"
        "  name: demo\n"
        "spec:\n"
        "  containers:\n"
        "    - name: app\n"
        "      image: nginx\n"
        "      securityContext:\n"
        "        privileged: true\n"
    )
    result = validate_source("demo.yaml", sample)
    security_findings = [
        finding for finding in result["findings"] if finding["rule_family"] == "security"
    ]
    assert len(security_findings) == len(
        {finding["rule_id"] for finding in security_findings}
    )
    assert any(
        finding["rule_id"] == "security_privileged_container"
        for finding in security_findings
    )
