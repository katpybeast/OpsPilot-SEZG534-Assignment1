from __future__ import annotations

ACTIVE_RULES = {
    "ci_cd": [
        "ci_cd_dependency_failure",
        "ci_cd_test_failure",
        "ci_cd_build_failure",
    ],
    "docker": [
        "docker_root_user",
        "docker_exposed_port_22",
        "docker_missing_security_user",
    ],
    "kubernetes": [
        "k8s_invalid_yaml",
        "k8s_missing_resource_limits",
        "k8s_privileged_container",
    ],
    "security": [
        "security_privileged_container",
        "security_missing_resource_limits",
    ],
}

ACTIVE_RULE_IDS = {family: set(rule_ids) for family, rule_ids in ACTIVE_RULES.items()}


def get_active_rule_ids(family: str | None = None) -> list[str]:
    if family is None:
        flat: list[str] = []
        for rule_ids in ACTIVE_RULES.values():
            flat.extend(rule_ids)
        return flat
    return list(ACTIVE_RULES.get(family, []))
