import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

base = Path("evidence/full-evaluation")
data = json.loads((base / "eval-results.json").read_text(encoding="utf-8"))

attempts = data["attempt_results"]
generated = sum(a["generation_status"] == "generated" for a in attempts)
failed = len(attempts) - generated

lines = [
    "# OpsPilot AI — Full Evaluation Report",
    "",
    f"Evaluation date: {datetime.now(timezone.utc).date()}",
    "",
    "## Overall result",
    "",
    f"- **Status:** {data['evaluation_status']}",
    f"- Dataset cases: {data['dataset_case_count']}",
    f"- Planned attempts: {data['attempt_count']}",
    f"- Successful generations: {generated}",
    f"- Failed generations: {failed}",
    f"- Semantic score: {data['semantic_score_percent']}%",
    f"- Required threshold: {data['threshold_percent']}%",
    "",
    "## Validation results",
    "",
    f"- Schema failures: {data['schema_failure_count']}",
    f"- Invariant failures: {data['invariant_failure_count']}",
    f"- Safety failures: {data['safety_failure_count']}",
    f"- Model failures: {data['model_failure_count']}",
    "",
    "## Generation status breakdown",
    "",
]

for status, count in Counter(a["generation_status"] for a in attempts).items():
    lines.append(f"- {status}: {count}")

lines += [
    "",
    "## Safety failures",
    "",
]

for a in attempts:
    if a["safety_status"] == "failed":
        lines.append(
            f"- {a['case_id']}, attempt {a['attempt_number']}: "
            + ", ".join(a["safety_failure_reasons"])
        )

lines += [
    "",
    "## Interpretation",
    "",
    "The evaluation did not meet the required acceptance threshold. "
    "The 33 model-generation failures reduced the aggregate score. "
    "All successfully generated responses passed schema validation, "
    "but one adversarial case failed a safety check.",
    "",
    "The single successful schema-retry smoke test demonstrates that "
    "the structured-output change can produce a schema-valid response. "
    "It does not establish reliable performance across the full dataset.",
    "",
    "## Limitations and outstanding decisions",
    "",
    "- Underlying error codes for failed generations were not retained "
    "in the evaluation report.",
    "- Resource verification remains pending.",
    "- Compatibility with the constitutional 8 GB target remains unresolved.",
    "- Final human acceptance has not been granted.",
    "",
    "## Evidence locations",
    "",
    "- eval-results.json",
    "- evaluation.log",
    "- harness-log.md",
    "- responses/",
    "- ../live-smoke-test/",
    "- ../live-smoke-test-retry-01/",
    "",
    "## Human decision",
    "",
    "REJECT — the current evaluation does not meet the 80% threshold. "
    "Further remediation and reevaluation are required before acceptance.",
]

out = base / "FINAL-EVALUATION-REPORT.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Created:", out)
print("Score:", data["semantic_score_percent"], "%")
print("Status:", data["evaluation_status"])
