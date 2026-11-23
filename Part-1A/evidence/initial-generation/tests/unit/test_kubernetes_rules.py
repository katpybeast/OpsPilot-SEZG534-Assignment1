from app.validators.kubernetes_validator import validate_kubernetes_contents


def test_kubernetes_invalid_yaml_detected():
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
    findings = validate_kubernetes_contents(sample)
    assert any(
        item.rule_id in {"k8s_privileged_container", "k8s_missing_resource_limits"}
        for item in findings
    )


def test_kubernetes_missing_limits_detected():
    sample = (
        "apiVersion: v1\n"
        "kind: Pod\n"
        "metadata:\n"
        "  name: demo\n"
        "spec:\n"
        "  containers:\n"
        "    - name: app\n"
        "      image: nginx\n"
    )
    findings = validate_kubernetes_contents(sample)
    assert any(item.rule_id == "k8s_missing_resource_limits" for item in findings)
