import time

from app.services.validation_service import validate_source


def test_validation_is_fast_enough_for_representative_samples():
    log_payload = ("failed to resolve dependency\n" * 65000)[: 1_048_576]
    k8s_payload = (
        "apiVersion: v1\n"
        "kind: Pod\n"
        "metadata:\n"
        "  name: demo\n"
        "spec:\n"
        "  containers:\n"
        "    - name: app\n"
        "      image: nginx\n" * 2000
    )

    start = time.perf_counter()
    log_result = validate_source("sample.log", log_payload)
    log_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    k8s_result = validate_source("sample.yaml", k8s_payload)
    k8s_elapsed = time.perf_counter() - start

    assert log_result["summary_status"] == "FAIL"
    assert k8s_result["summary_status"] in {"FAIL", "WARNING"}
    assert log_elapsed < 5.0
    assert k8s_elapsed < 5.0
