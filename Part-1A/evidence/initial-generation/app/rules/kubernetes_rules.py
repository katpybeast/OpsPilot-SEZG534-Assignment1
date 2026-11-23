from __future__ import annotations

from typing import Any

import yaml

from app.models.finding import Finding


def evaluate_kubernetes_rules(yaml_text: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        docs = list(yaml.safe_load_all(yaml_text))
    except yaml.YAMLError as exc:  # pragma: no cover - exercised by validator tests
        findings.append(
            Finding(
                rule_id="k8s_invalid_yaml",
                rule_family="kubernetes",
                severity="FAIL",
                status="FAIL",
                description="Kubernetes YAML is malformed and cannot be parsed.",
                evidence=str(exc),
                location="yaml",
            )
        )
        return findings

    for idx, doc in enumerate(docs, start=1):
        if not isinstance(doc, dict):
            continue
        for kind, resource in _iter_resources(doc):
            if _has_privileged_container(resource):
                findings.append(
                    Finding(
                        rule_id="k8s_privileged_container",
                        rule_family="kubernetes",
                        severity="FAIL",
                        status="FAIL",
                        description=f"{kind} uses privileged containers.",
                        evidence=f"Resource {kind} has privileged=true.",
                        location=f"{kind}:{idx}",
                    )
                )
            if _missing_limits(resource):
                findings.append(
                    Finding(
                        rule_id="k8s_missing_resource_limits",
                        rule_family="kubernetes",
                        severity="WARNING",
                        status="WARNING",
                        description=f"{kind} does not define CPU or memory limits.",
                        evidence=f"Resource {kind} is missing resource limits.",
                        location=f"{kind}:{idx}",
                    )
                )
    return findings


def _iter_resources(document: dict[str, Any]):
    kind = document.get("kind")
    if kind:
        yield kind, document
    for _, value in document.items():
        if isinstance(value, dict) and value.get("kind"):
            yield value.get("kind"), value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and item.get("kind"):
                    yield item.get("kind"), item


def _has_privileged_container(resource: dict[str, Any]) -> bool:
    if "spec" not in resource:
        return False
    spec = resource["spec"]
    if isinstance(spec, dict):
        containers = spec.get("containers", [])
        for container in containers:
            if isinstance(container, dict):
                sec = container.get("securityContext", {})
                if isinstance(sec, dict) and sec.get("privileged") is True:
                    return True
    return False


def _missing_limits(resource: dict[str, Any]) -> bool:
    if "spec" not in resource:
        return True
    spec = resource["spec"]
    if not isinstance(spec, dict):
        return True
    containers = spec.get("containers", [])
    if not containers:
        return True
    for container in containers:
        if not isinstance(container, dict):
            continue
        resources = container.get("resources", {})
        if not isinstance(resources, dict):
            return True
        limits = resources.get("limits", {})
        if not isinstance(limits, dict):
            return True
        if limits.get("cpu") or limits.get("memory"):
            return False
    return True
