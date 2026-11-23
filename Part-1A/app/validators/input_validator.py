from __future__ import annotations

from pathlib import Path

from app.limits import MAX_FILE_SIZE_BYTES

SUPPORTED_TYPES = {
    "ci_log": {".log"},
    "dockerfile": {".dockerfile", ".docker", "dockerfile"},
    "kubernetes_yaml": {".yaml", ".yml"},
}


def validate_uploaded_file(
    file_name: str,
    content: bytes | str,
    content_type: str | None = None,
) -> tuple[str, bytes]:
    if content is None:
        raise ValueError("Uploaded content is missing.")
    if isinstance(content, str):
        payload = content.encode("utf-8")
    else:
        payload = content

    if not payload:
        raise ValueError("The uploaded file is empty.")
    if len(payload) > MAX_FILE_SIZE_BYTES:
        raise ValueError("The uploaded file exceeds the 1 MiB limit.")

    file_name = file_name or "upload"
    suffix = Path(file_name).suffix.lower()
    source_type = _detect_source_type(file_name, suffix, content_type)
    if source_type is None:
        raise ValueError(
            "Unsupported file type. Use a plain-text log, Dockerfile, or "
            "Kubernetes YAML file."
        )
    return source_type, payload


def _detect_source_type(file_name: str, suffix: str, content_type: str | None) -> str | None:
    lower_name = file_name.lower()
    if lower_name.endswith("dockerfile") or suffix in SUPPORTED_TYPES["dockerfile"]:
        return "dockerfile"
    if suffix in SUPPORTED_TYPES["ci_log"] or lower_name.endswith(".log"):
        return "ci_log"
    if suffix in SUPPORTED_TYPES["kubernetes_yaml"]:
        return "kubernetes_yaml"
    if content_type and "yaml" in content_type.lower():
        return "kubernetes_yaml"
    return None
