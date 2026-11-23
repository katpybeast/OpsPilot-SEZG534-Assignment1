
import json
import hashlib
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from opspilot.evaluation.runner import EvaluationRunner
from opspilot.model_client import OllamaClient

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "evidence" / "full-evaluation"
RESPONSES = OUT / "responses"

OUT.mkdir(parents=True, exist_ok=False)
RESPONSES.mkdir()

log_path = OUT / "harness-log.md"
report_path = OUT / "eval-results.json"

logging.basicConfig(
    filename=OUT / "evaluation.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def log(message):
    print(message, flush=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(message + "\n")

log("# OpsPilot AI Full Evaluation")
log(f"Started UTC: {datetime.now(timezone.utc).isoformat()}")
log("Mode: 17 cases, 3 attempts per case, local Ollama inference")

runner = EvaluationRunner(threshold_percent=80.0)

ok, dataset = runner.load_and_validate_dataset()
if not ok:
    log("DATASET VALIDATION FAILED: " + str(dataset))
    sys.exit(2)

case_count = len(dataset["cases"])
attempt_count = case_count * 3
log(f"Dataset validated: {case_count} cases; planned attempts: {attempt_count}")

# Wrap the single-attempt method to retain genuine outputs and provenance.
original_method = runner._run_single_attempt
capture = {"count": 0, "provenance": None}

def captured_attempt(client, case_id, attempt_num, case_input, case_dict):
    original_generate = client.generate

    def capture_generate(text):
        result = original_generate(text)
        capture["provenance"] = result.provenance.__dict__
        filename = f"{case_id}-attempt-{attempt_num}.json"
        artifact = {
            "case_id": case_id,
            "attempt_number": attempt_num,
            "response": result.response,
            "response_sha256": result.response_sha256,
            "provenance": result.provenance.__dict__,
            "captured_utc": datetime.now(timezone.utc).isoformat(),
        }
        path = RESPONSES / filename
        path.write_text(
            json.dumps(artifact, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        capture["count"] += 1
        log(f"Captured {capture['count']}/{attempt_count}: {filename}")
        return result

    client.generate = capture_generate
    try:
        return original_method(client, case_id, attempt_num, case_input, case_dict)
    finally:
        client.generate = original_generate

runner._run_single_attempt = captured_attempt

try:
    log("Starting genuine model evaluation.")
    report = runner.run_evaluation(dataset)

    report["captured_response_count"] = capture["count"]
    report["captured_model_provenance"] = capture["provenance"]
    report["started_utc"] = datetime.now(timezone.utc).isoformat()

    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    log(f"Evaluation status: {report['evaluation_status']}")
    log(f"Attempts: {report['attempt_count']}")
    log(f"Responses captured: {capture['count']}")
    log(f"Semantic score: {report['semantic_score_percent']}%")
    log(f"Schema failures: {report['schema_failure_count']}")
    log(f"Invariant failures: {report['invariant_failure_count']}")
    log(f"Safety failures: {report['safety_failure_count']}")
    log(f"Model failures: {report['model_failure_count']}")
    log(f"Report: {report_path}")

    if capture["count"] != attempt_count - report["model_failure_count"]:
        log("WARNING: Captured response count differs from successful generation count.")

    log(f"Completed UTC: {datetime.now(timezone.utc).isoformat()}")

except Exception as exc:
    log(f"FATAL EVALUATION ERROR: {type(exc).__name__}: {exc}")
    raise
