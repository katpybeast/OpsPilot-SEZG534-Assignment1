# Tasks: OpsPilot AI — Intelligent DevOps Log Explainer

**Input**: Design documents from `specs/001-explain-ci-logs/`  
**Branch**: `001-explain-ci-logs`  
**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), and [quickstart.md](quickstart.md)

**Organization**: Tasks are grouped by the 12 implementation phases requested. `[US1]`, `[US2]`, and `[US3]` preserve traceability to the three approved user stories. All tasks remain unchecked; no implementation, test, or evaluation result is claimed.

**Test policy**: Pytest and Ruff are required by the approved specification and constitution. Test tasks are included before their corresponding implementation tasks where practical. The evaluation dataset is synthetic and versioned; tests and evaluation results must be recorded only after they are actually run.

**Task format**: `- [ ] T### [P?] [US#?] Description with exact file path(s)`

- `[P]` means the task can run in parallel with other marked tasks because it edits independent files and has no unmet task dependency.
- `[US1]` is “Explain a CI/CD Failure”; `[US2]` is “Handle Insufficient, Invalid, and Adversarial Logs Safely”; `[US3]` is “Evaluate, Review, and Repair Explanations.”
- Every task has one unique sequential ID and identifies its output or test file path.

## Phase 1: Project setup and dependencies

**Purpose**: Establish a reproducible Windows project baseline before application implementation.

- [ ] T001 Record the pre-implementation repository revision in `docs/evidence/initial-state.md`; if Git metadata is unavailable, explicitly state that no Git repository/revision is available. Preserve the sanitized workspace file inventory and starting application state, with no raw logs, secrets, or personal data; complete before changing application source.
- [ ] T002 Create the planned Python package and entry-point skeleton in `app.py`, `opspilot/__init__.py`, `opspilot/validation/__init__.py`, and `opspilot/evaluation/__init__.py` without adding feature behavior.
- [ ] T003 Declare free Python runtime dependencies (Streamlit and `jsonschema`) with Windows-compatible constraints in `requirements.txt`; Ollama is a separately provisioned local runtime, not a Python model package; exclude cloud clients, paid APIs, and database dependencies.
- [ ] T004 Declare development dependencies and tool configuration in `requirements-dev.txt` and `pyproject.toml` for Pytest, Ruff lint/format, and Python 3.11+.
- [ ] T005 [P] Add `.gitignore` entries for `.venv/`, Python caches, pytest/Ruff caches, and local scratch files while keeping sanitized evaluation evidence versionable.
- [ ] T006 [P] Configure `.streamlit/config.toml` to bind Streamlit to `127.0.0.1` and disable usage statistics; do not enable external assets, hosting, or content caching.

## Phase 2: JSON schemas and data models

**Purpose**: Establish typed application/evaluation entities and regression coverage for the approved contract schemas.

- [ ] T007 [P] [US1] Add contract tests in `tests/contract/test_response_schema.py` that load `specs/001-explain-ci-logs/contracts/explanation-response.schema.json` and assert the exact eight required keys, enums, types, lengths, array bounds, `additionalProperties: false`, and each status-specific rule.
- [ ] T008 [P] [US3] Add contract tests in `tests/contract/test_evaluation_schemas.py` for `specs/001-explain-ci-logs/contracts/evaluation-case.schema.json`, `evaluation-dataset.schema.json`, and `evaluation-report.schema.json`, including required fields, confidence/status conditionals, minimum 15 cases, finite `SAFETY-1` reason codes (reject unknown codes), independent evaluation/system-acceptance states, resource/constitution conditions, and human-review states.
- [ ] T009 Define typed entities in `opspilot/models.py` for `LogSubmission`, `ExplanationResponse`, `ModelProvenance`, `GenerationConfig`, `EvidenceCandidate`, `EvaluationCase`, `EvaluationAttemptResult`, and `EvaluationRun`; preserve the exact response fields and limits from the response schema.
- [ ] T010 [P] Define centralized application/prompt, model-configuration, and rubric version identifiers in `opspilot/versions.py` so reports identify the evaluated candidate without implying deterministic generated outputs.

## Phase 3: Local stochastic model generation

**Purpose**: Implement local Ollama inference as the primary explanation generator, with deterministic evidence extraction and safe failure behavior.

- [ ] T011 [P] [US1] Write local-model client tests in `tests/unit/test_model_client.py` for Ollama loopback requests, nonzero temperature, omitted seed, model/config provenance, exactly three independent attempts per case, and unavailable/timeout/invalid-output failures.
- [ ] T012 [US1] Implement the Ollama loopback client in `opspilot/model_client.py` for the proposed `qwen2.5:1.5b` model; record actual model/runtime/digest/settings and never pull/download a model or call a non-loopback endpoint at runtime.
- [ ] T013 [US1] Implement bounded prompt assembly and deterministic evidence extraction in `opspilot/prompting.py` and `opspilot/evidence.py`; mark log text untrusted, preserve evidence grounding, and do not turn log text into instructions, code, regexes, or commands.
- [ ] T014 [US1] Implement strict response parsing and safe response handling in `opspilot/response.py`; validate model-generated fields without rule-based successful fallback, and map model failure to safe `analysis_error` or a failed evaluation attempt.

## Phase 4: Safety and adversarial input handling

**Purpose**: Enforce input limits, redact recognizable sensitive data, and ensure adversarial content remains inert.

- [ ] T015 [P] [US2] Write boundary tests in `tests/safety/test_input_validation.py` for empty/whitespace input, 262,144 UTF-8 bytes, one byte over limit, multibyte text at the limit, NUL, more than 10% non-whitespace control characters, and allowed newline/carriage-return/tab.
- [ ] T016 [P] [US2] Write adversarial/redaction tests in `tests/safety/test_adversarial_logs.py` using synthetic canary secrets, prompt-injection instructions, shell/code/URL text, hidden-instruction requests, conflicting signals, and unsafe-action requests; assert no execution, instruction following, or sensitive echo and map each safety failure to the applicable `SAFETY-1` code.
- [ ] T017 [US2] Implement UTF-8 byte, empty-input, malformed-input, and control-character validation in `opspilot/input_validation.py`; reject inputs over 262,144 bytes without truncation and return the defined safe invalid-input response path.
- [ ] T018 [US2] Implement deterministic secret-like-value redaction in `opspilot/redaction.py` before evidence/report construction; keep raw text transient, do not log/cache/persist it, and document that redaction is defense-in-depth rather than guaranteed detection of every secret.
- [ ] T019 [US2] Add privacy/no-execution regression coverage in `tests/safety/test_data_handling.py` to assert that raw submissions and exception details do not enter caches, logs, reports, exports, or persistent storage.

## Phase 5: Streamlit user interface

**Purpose**: Provide a single local paste-and-explain flow whose machine-readable result is the strict JSON contract.

- [ ] T020 [P] [US1] Write Streamlit integration tests in `tests/integration/test_streamlit_ui.py` for pasted valid logs, explicit submit, byte-limit feedback, one JSON response, and reset behavior using synthetic inputs.
- [ ] T021 [US1] Implement the local page in `opspilot/ui.py` with product purpose, privacy/no-secrets notice, pasted-log text area, UTF-8 byte count, explicit Explain action, and a readable/copyable JSON result with no second prose diagnosis or command-execution control.
- [ ] T022 [US1] Connect `app.py` to the input boundary, local Ollama model service, independent validators, and validated JSON response; ensure model failures are safe and never trigger rule-based successful fallback.

## Phase 6: Evaluation dataset with at least 15 meaningful cases

**Purpose**: Author synthetic fixtures and a preflight gate that enforce category and scenario coverage before evaluation begins.

- [ ] T023 [P] [US3] Write dataset tests in `tests/evaluation/test_dataset.py` for unique case IDs, at least 15 non-empty input-valid cases, exactly one `primary_category` per case, at least two primary cases for each category, primary-category membership in `expected_categories`, `UNKNOWN` requiring partial credit false, all seven exact tags, required fields, and synthetic/sanitized content.
- [ ] T024 [US3] Create `data/evaluation_cases.json` with at least 15 distinct meaningful non-empty synthetic submissions that pass input validation; include at least two cases per `primary_category` across all six values and cover all seven tags. Include the exact resource fixtures `resource-build-001`, `resource-dependency-001`, and `resource-test-001` from the spec as valid cases with matching input strings and primary categories BUILD, DEPENDENCY, and TEST. Invalid application submissions remain separate safety tests.
- [ ] T025 [US3] Implement dataset loading and preflight in `opspilot/evaluation/dataset.py`; validate checked-in schemas and reject empty/input-invalid fixtures, missing metadata, duplicate IDs, primary-category mismatches, invalid `UNKNOWN` partial-credit combinations, category/tag gaps, more than 262,144 UTF-8 bytes, or prohibited sensitive content before any model call.

## Phase 7: Independent schema validation

**Purpose**: Validate the serialized JSON independently from response construction before treating it as a valid explanation.

- [ ] T026 [P] [US1] Write strict parser and response-validation tests in `tests/contract/test_output_validation.py` for duplicate keys, `NaN`/infinities, malformed JSON, trailing prose, non-object top levels, missing/extra fields, wrong types, enum/length violations, and each status-dependent rule.
- [ ] T027 [US1] Implement `opspilot/validation/schema.py` using a local Draft 2020-12 validator and the canonical schema at `specs/001-explain-ci-logs/contracts/explanation-response.schema.json`; check the schema itself, reject duplicate JSON keys/non-standard constants, prohibit remote reference resolution, and serialize with non-finite numbers disabled.
- [ ] T028 [US1] Integrate the serialized-output parse and independent schema gate into `opspilot/response.py` before JSON is rendered as valid; convert validation failure to a safe failure path without displaying invalid content as an accepted explanation.

## Phase 8: Structural invariant tests

**Purpose**: Enforce cross-field, evidence-grounding, deterministic validation, and safety invariants separately from stochastic generation and semantic scoring.

- [ ] T029 [P] [US2] Write invariant tests in `tests/contract/test_invariants.py` for all statuses; evidence-to-sanitized-input grounding; confidence/status bands; actions; redaction; nonzero-temperature/no-seed provenance; and rejection of unsupported certainty. Do not assert repeated-output equality or diversity.
- [ ] T030 [US1] Implement independent cross-field and input-relative checks in `opspilot/validation/invariants.py`; verify status/category/confidence/needs-more-information relationships, evidence grounding, array constraints, sanitized content, and deterministic validator behavior without relying on semantic scores or requiring generated fields to repeat.
- [ ] T031 [US2] Gate UI/runner acceptance on `opspilot/validation/invariants.py`; invalid schema or invariant output must be rejected or handled safely and must never be treated as a valid explanation.

## Phase 9: Semantic quality scoring with the 80% threshold

**Purpose**: Implement the fixed deterministic rubric and aggregate threshold without weakening acceptance criteria.

- [ ] T032 [P] [US3] Write rubric unit tests in `tests/evaluation/test_scoring.py` for category, evidence, root-cause, action, and uncertainty points (0–2 each); exact confidence matching; empty-array and partial-credit predicates; zero points for failed/unparseable/schema-invalid attempts with each 10-point attempt denominator retained; zero-case preflight behavior without division; unrounded threshold comparison; and scores below, exactly at, and above 80%.
- [ ] T033 [US3] Implement deterministic scoring and aggregation in `opspilot/evaluation/scoring.py` with five 0–2 dimensions per attempt, literal normalized case predicates, explicit empty-array and single-confidence rules from `spec.md`, exactly `100 × total earned points / (30 × case_count)` (equivalently `100 × total earned points / (10 × attempt_count)`) after successful preflight, score 0 without division for zero attempts, six-decimal report rounding, fixed rubric version, and a non-configurable acceptance floor of 80% or higher; hard gates must independently fail the run.

## Phase 10: Unified evaluation harness and structured reports

**Purpose**: Execute the required ordered pipeline and preserve sanitized attempt-level and run-level evidence; the report uses three flat attempt records per case grouped by `case_id`, without a separate case-summary object.

- [ ] T034 [P] [US3] Write evaluation-report contract and invariant tests in `tests/evaluation/test_report.py` for model/runtime/config provenance, three attempt results per case, immutable per-attempt artifacts/digests, count reconciliation, per-attempt point sums, aggregate arithmetic, required `safety_catalog_version: SAFETY-1`, the four exact `SAFETY-1` codes, rejection of unknown safety versions/codes, safety status/reason/count reconciliation independent of schema/invariant outcomes, failed-ID/failure correspondence, below-80% semantic failure per sub-10-point attempt, dataset threshold failure, preflight failures, and automated evaluation versus overall system-acceptance states.
- [ ] T035 [P] [US3] Write harness integration tests in `tests/evaluation/test_runner.py` for `dataset → three independent local-model calls per case → capture → schema validation → structural invariants → independent safety validation → per-attempt semantic scoring → aggregate → automated evaluation status`; do not compare response equality or require diversity. Test every `SAFETY-1` validation check and reject unknown codes. Verify automated `PASS` does not set overall acceptance and that resource/constitution gates remain separately pending or blocked.
- [ ] T036 [US3] Implement immutable sanitized report construction in `opspilot/evaluation/report.py` using `specs/001-explain-ci-logs/contracts/evaluation-report.schema.json`; include dataset/rubric/application/model/runtime provenance, `safety_catalog_version: SAFETY-1`, effective generation settings, case and attempt counts/results, sanitized response/safe-failure artifact paths and hashes, threshold/score, schema/invariant/safety/model failure counts, each attempt's independent safety status and allowed `SAFETY-1` reason codes, failed case IDs, separate automated/resource/constitution/system-acceptance statuses, and resource/constitution evidence references. Reject unknown safety versions/codes. An automated `PASS` MUST NOT imply system acceptance. Never persist raw prompts/logs, secrets, personal identifiers, stack traces, or exception text.
- [ ] T037 [US3] Implement the ordered local harness in `opspilot/evaluation/runner.py`; preflight dataset and local model provenance, make exactly three independent Ollama calls per case, then run strict parsing/schema validation, structural invariant checks, an independent safety validator using the four `SAFETY-1` checks, per-attempt deterministic scoring, and automated PASS/FAIL calculation. Report resource and constitution acceptance statuses independently; they MUST NOT change or be inferred from automated evaluation status.
- [ ] T038 [US3] Add the Windows command-line entry point in `opspilot/evaluation/__main__.py` matching `quickstart.md`; accept local dataset/output paths only, make no external requests, and preserve each run report rather than overwrite prior failures.

## Phase 11: Human review, repair and reevaluation workflow

**Purpose**: Keep automated evaluation advisory and require a recorded human decision for every run.

- [ ] T039 [P] [US3] Write human-review state tests in `tests/evaluation/test_review.py` for human review after every automated outcome, approval only after automated gates plus resource and constitution-compatibility prerequisites pass, rejection/request-repair recording, fixed non-identifying `human_reviewer` role, the exact allowed reason-code enum, no free-form identity fields, and separation of `evaluation_status` from `system_acceptance_status`.
- [ ] T040 [P] [US3] Write repair/reevaluation preservation tests in `tests/evaluation/test_reevaluation.py` asserting that repair creates a new run, retains the original failure report, preserves dataset/rubric/threshold versions, and reruns the complete affected pipeline.
- [ ] T041 [US3] Implement explicit local review recording in `opspilot/evaluation/review.py`; support approved, rejected, and request-repair decisions using only `reviewer_role: "human_reviewer"` and the schema enum; do not store personal identifiers or free-form rationale. Human approval may complete overall system acceptance only when automated evaluation is `PASS`, resource status is `PASS`, and documented constitution compatibility is `COMPATIBLE`; it MUST NOT infer those statuses from an evaluation score.
- [ ] T042 [US3] Implement repair linkage and full reevaluation orchestration in `opspilot/evaluation/review.py` and `opspilot/evaluation/runner.py`; never rewrite prior reports, change the 80% floor, selectively omit cases, or treat a repaired candidate as accepted before a new automated pass and human approval.

## Phase 12: Documentation and final verification

**Purpose**: Document reproducible Windows workflows and collect final, sanitized acceptance evidence after implementation is complete. The separately authorized spike may collect preliminary evidence earlier; T053–T061 follow the governance/resource ordering below.

- [ ] T043 [P] [US2] Add Windows-local/network regression tests in `tests/integration/test_local_only.py` for Streamlit/Ollama loopback-only configuration, disabled usage statistics, no external runtime calls, and no raw-log persistence.
- [ ] T044 [P] Update `specs/001-explain-ci-logs/quickstart.md` to document the implemented PowerShell setup, separately provisioned Ollama/model, loopback preflight, Streamlit launch, Pytest/Ruff commands, local evaluation, offline setup, resource checks, and human-review/repair steps without claiming unrun outcomes.
- [ ] T045 [P] Create or update `README.md` with project purpose, supported Windows/Python environment, local-only/privacy boundaries, free dependency policy, and links to the specification, plan, contracts, dataset, and quickstart.
- [ ] T046 Create `docs/evidence/README.md` describing evidence naming, version provenance, sanitization, preservation of failures/repairs, and the prohibition on recording raw logs or fabricated outcomes.
- [ ] T047 Run the documented Windows setup, full Pytest suite, Ruff lint, and Ruff format check; record actual commands, environment, outcomes, and any justified exceptions in `docs/evidence/verification.md` without weakening criteria; include the dependency-license audit reference.
- [ ] T048 Run the complete evaluation on the documented Windows 8 GB reference laptop; retain the actual sanitized flat per-attempt/run reports under `reports/evaluations/`, including all three attempt records per case, failures, and repairs, with no raw input or sensitive values.
- [ ] T049 Measure SC-005 end-to-end from submission to schema-validated JSON with the model already loaded; verify at least `ceil(0.95 × N)` of the `N` valid fixed-dataset fixtures complete within 5 seconds, record cold-load separately, and document hardware/runtime context and actual timing in `reports/evaluations/performance.json` without inferring or fabricating a pass.
- [ ] T050 Obtain and record a human review decision for every final automated evaluation run in its report under `reports/evaluations/`, using only the fixed reviewer role and decision reason code. Keep automated evaluation and system acceptance statuses separate; `ACCEPTED` requires automated PASS, verified SC-009 resource compliance, documented constitutional compatibility, and explicit human approval.
- [ ] T051 Complete a requirement-to-task/verification audit in `docs/evidence/acceptance-review.md`; map all FR-001–FR-025, TC-001–TC-005, and SC-001–SC-009, verify no criterion or threshold was weakened, and list unresolved failures rather than waiving them.
- [ ] T052 Audit direct and transitive Python dependencies for no-cost use, acceptable license terms, and local installability; record package names, versions, license identifiers, and provenance in `docs/evidence/dependency-audit.md`, and fail review for paid, unlicensed, or cloud-runtime dependencies.
- [ ] T053 [US3] Verify the provisioned Ollama runtime and exact `qwen2.5:1.5b` artifact version, digest, and license; record setup provenance in `docs/evidence/model-provenance.md` and confirm the application/evaluator will not pull or update models at runtime. Before the spike measurement, verify the actual implemented application and evaluator entry/model-access paths, not placeholders. Recheck those paths against the final candidate whenever later changes affect them, before final T054 and acceptance.
- [ ] T054 [US3] Execute the fixed SC-009 benchmark protocol from `spec.md` using dataset cases `resource-build-001`, `resource-dependency-001`, and `resource-test-001`, exact context 4096/output 768/temperature 0.7/no seed. Run three cold-start sessions (terminate app/Ollama/model-runner between sessions; invoke each fixture once/session) and one warm session (one unmeasured warm-up per fixture, then three measured calls per fixture). Sample once per second the combined working sets of unique PIDs in both process trees throughout startup and inference. Require peak ≤2 GiB and record inputs, calls, cold/warm condition, OS/hardware, model/runtime/digest, config, PID-selection/sampling method, per-trial samples/maxima, failures, and overall maximum in `docs/evidence/model-resource-acceptance.md`; do not invent results.
- [ ] T055 [US3] If T054 exceeds 2 GiB, block acceptance and document a smaller-model/quantization investigation or a justified specification revision through governance; repeat the identical T054 workload and record revised artifact/configuration and measurements in `docs/evidence/model-resource-investigation.md`. If the screen passes, record that fact only; it is not proof of constitutional compatibility. Do not claim the proposed Qwen model meets the limit before measurement.
- [ ] T056 [US3] Before feature application source implementation, obtain and record the project owner's decision in `docs/evidence/constitution-compatibility.md` on whether to authorize a measurement-only resource spike for the proposed local model, or instead require architecture redesign/formal constitution amendment. The 2 GiB screen MUST NOT be represented as proof of constitutional compatibility; no constitution amendment is made by this task.
- [ ] T057 [US3] After the final application candidate has completed T054 and T055 as applicable, obtain and record the project owner's **final** determination in `docs/evidence/constitution-compatibility.md` on whether that measured architecture satisfies the constitution's 8 GB/non-resource-intensive requirement. Until compatibility is explicitly recorded, block design and overall acceptance. If incompatible or indeterminate, require redesign or a separately approved formal constitution amendment. Revisit measurement and the determination if subsequent changes make the evidence inapplicable. This task does not amend the constitution.
- [ ] T058 [US3] After the T056 owner decision, obtain and record separate explicit owner approval for a bounded implementation-and-measurement spike on the documented 15.7 GiB Windows computer. The scope is limited to T001 baseline recording, T024 fixtures, the minimum runnable app and real evaluator/model-access paths needed for T053, corresponding provenance and safety checks, preliminary measurement, and sanitized evidence. Use the same three fixtures, model configuration, cold/warm schedule and sampling method as T054, measuring combined application and Ollama/model-runner working sets against the unchanged ≤2 GiB threshold. Label results **PRELIMINARY — NOT FINAL SC-009 EVIDENCE**. They do not complete T054, establish 8 GB constitutional compatibility, or authorize broader implementation. Installation or provisioning requires any separately necessary authorization. Task completion requires each task’s own work, evidence and permission.
- [ ] T059 [US3] After T058 approval and the preliminary measurement, obtain and record the owner’s provisional feasibility assessment. The measurement uses the same three fixtures, model configuration, cold/warm schedule and sampling method as T054, but measures combined application and Ollama/model-runner working sets on the 15.7 GiB computer. Label its results **PRELIMINARY — NOT FINAL SC-009 EVIDENCE**. They do not complete T054, establish 8 GB constitutional compatibility, or authorize broader implementation. If the observed maximum exceeds 2 GiB, block acceptance and investigate before a positive provisional assessment. If the assessment is incompatible or indeterminate, require redesign or a separately approved governance route. Broader implementation requires separate T060 approval.
- [ ] T060 [US3] After a positive provisional T059 determination, obtain and record a separate explicit project-owner decision in `docs/evidence/constitution-compatibility.md` on broader implementation. Record the approved scope and any separately permitted task completion. Do not begin work outside T058's bounded scope without explicit approval. This decision does not establish final constitutional compatibility, complete T054 or T057, or authorize acceptance.
- [ ] T061 [US3] Before final T054, identify the actual Windows 8 GB benchmark target and record its hardware, Windows version and installed RAM in bytes in `docs/evidence/constitution-compatibility.md`, using authorized, sanitized system-generated evidence from that target. Record the source; a machine description alone is insufficient. The separately reported 15.7 GiB computer is not that target. If a suitable target is unavailable or unverified, final T054 and acceptance remain blocked unless a separately approved governance route resolves the applicable requirements. Do not silently waive the 8 GB requirement.

## Requirement-to-task traceability

| Requirement | Tasks |
|---|---|
| FR-001 | T020–T022, T045 |
| FR-002 | T015, T017, T023–T025 |
| FR-003 | T011–T014, T023–T025 |
| FR-004 | T016, T018, T029–T030, T036 |
| FR-005 | T011, T013–T014 |
| FR-006 | T011, T014 |
| FR-007 | T011, T013–T014 |
| FR-008 | T007, T026–T028, T020–T022 |
| FR-009 | T016–T019, T029–T031, T043 |
| FR-010 | T003, T005–T006, T043–T045, T047 |
| FR-011 | T001, T016, T018–T019, T036, T043, T045–T046 |
| FR-012 | T011, T013, T032–T033, T035–T037 |
| FR-013 | T007, T026–T031 |
| FR-014 | T008, T023–T025 |
| FR-015 | T008, T023–T025, T032 |
| FR-016 | T026–T037 |
| FR-017 | T032–T033 |
| FR-018 | T032–T033 |
| FR-019 | T023–T025, T035–T037 |
| FR-020 | T034, T036–T038 |
| FR-021 | T039, T041, T050 |
| FR-022 | T040, T042, T048–T050 |
| FR-023 | T001, T036, T040, T046–T051 |
| FR-024 | T009–T014, T032–T037, T053–T054 |
| FR-025 | T011–T014, T022, T035–T037, T053–T054 |
| TC-001 | T002, T006, T020–T022, T044–T045, T047 |
| TC-002 | T003, T005–T006, T043–T045, T047, T052–T055 |
| TC-003 | T011–T014, T032–T037, T044, T053–T061 |
| TC-004 | T004, T007–T008, T046–T047 |
| TC-005 | T001, T018–T019, T036, T046–T048 |

## Success-criteria-to-task traceability

| Success criterion | Verification tasks |
|---|---|
| SC-001 | T007, T026–T028, T034, T047 |
| SC-002 | T029, T035, T048 |
| SC-003 | T023–T025, T035 |
| SC-004 | T032–T037, T048 |
| SC-005 | T049, T054 |
| SC-006 | T039, T041, T050 |
| SC-007 | T019, T043, T047, T048, T054 |
| SC-008 | T025, T034–T036, T050–T051 |
| SC-009 | T054–T061 |

## Dependencies and execution order

### Phase dependencies

1. **Constitution gate and bounded spike**: Record the T056 decision, then obtain separate T058 approval before scoped implementation or application runs on the documented 15.7 GiB computer. Record the approved scope, target machine and safety procedures before that work. The existing measurement-only authorization does not authorize task completion; do not check off T056 or other tasks unless task completion is separately authorized and evidenced. Complete T001 before source changes. Within T058's approved scope, create the T024 fixtures, implement the candidate and minimum real evaluator paths, and complete T053 checks.
2. Phase 1 baseline/setup precedes source changes; T001 must be completed before application source changes.
3. Phase 2 contract/model tests and shared types precede local model, safety, UI, and evaluator work.
4. Phases 3 and 4 share the Phase 2 model foundation; the Ollama client and input-safety layer must both be ready before completing the UI integration.
5. Phase 5 UI depends on the response service and safety boundary. Phase 6 dataset work can proceed after shared models/contracts and must finish before the evaluation runner.
6. Phase 7 schema validation precedes Phase 8 invariant acceptance. Both independent gates precede scoring and the unified harness.
7. Phase 9 scoring and Phase 6 dataset preflight precede Phase 10 orchestration/reporting.
8. Phase 11 human decision and repair workflows depend on Phase 10 reports and runner; final Phase 12 verification depends on all prior phases. T053–T061 follow the governance/resource ordering below.
9. **Governance/resource ordering**: Measure the spike candidate on the 15.7 GiB computer using the same fixtures, model configuration, cold/warm schedule and sampling method as T054, and label results **PRELIMINARY — NOT FINAL SC-009 EVIDENCE**. If the screen exceeds 2 GiB, apply T055's investigation and repeat-measurement requirements; spike evidence does not complete T055. Record T059's provisional owner assessment; spike evidence does not complete final T054 or T057. If the assessment is incompatible or indeterminate, require redesign or a separately approved formal constitution amendment. A positive T059 assessment does not authorize broader implementation. Obtain separate T060 approval before work outside T058's scope. Before final T054, identify and verify the genuine 8 GB target under T061. Then recheck T053 where needed, run T054 on the final candidate, address T055 as applicable, and obtain T057's final owner determination before T050 acceptance. If T061 cannot verify a suitable 8 GB target, final T054 and acceptance remain blocked. An alternate machine, simulation, or owner authorization alone does not replace the target requirement. The owner may pursue a separately approved governance route; until it resolves the applicable requirements, final T054 and acceptance remain blocked. Keep the design and acceptance gates blocked until their required final evidence and decisions exist. T052 remains an explicit prerequisite for T047/T051. Automated evaluation T048 may report PASS independently, but must not set system acceptance.

### User-story dependencies and independent test criteria

- **US1 (P1; tasks T007, T011–T014, T020–T022, T026–T031)**: After setup and shared models, paste a synthetic supported failure and an unknown/insufficient log; each yields one strict JSON object with model-generated category/explanation, grounded evidence, safe actions, valid confidence bands, and no unsupported certainty. This slice is independently testable without running the evaluation harness.
- **US2 (P1; tasks T015–T019, T029–T031, T043)**: Submit empty, malformed, boundary, oversized, secret-canary, and instruction-like inputs; verify defined safe JSON states, redaction, no execution/instruction following, no raw-log persistence, and no external network call. This safety slice is independently testable with synthetic fixtures.
- **US3 (P2; tasks T008, T023–T025, T032–T042, T046–T061)**: Run the versioned dataset through three independent stochastic attempts per case, separate gates, and deterministic per-attempt rubric; automated PASS requires ≥15 cases, ≥2 cases per primary category, complete tag coverage, zero model/schema/invariant/safety failures, and ≥80%. Overall acceptance remains separate and requires resource evidence, constitutional compatibility, and human approval. Failure reports and repair reruns preserve every sanitized attempt artifact.

### Parallel opportunities

- After T001, T002–T006 are independent setup outputs; T005 and T006 are explicitly marked `[P]`.
- T007 and T008 are independent contract test files; T023's test can be prepared independently from later dataset authoring.
- T015 and T016 are independent safety test files; after they are specified, T017 and T018 may be implemented in separate modules.
- T034 and T035 are independent evaluation test files; T039 and T040 are separate human-workflow tests.
- Documentation tasks T044–T046 touch separate files and can proceed independently from one another, after interface/command details are stable.
- No task marked `[P]` depends on another unfinished task that edits the same file.

## Implementation strategy

### MVP

1. Record T056's owner decision and obtain separate T058 approval for the bounded application implementation-and-measurement spike on the documented 15.7 GiB computer. Record T001 before application source changes; perform T053 provenance checks, T024 fixture creation, and candidate implementation within the approved scope.
2. Measure the spike candidate using the same fixtures, model configuration, cold/warm schedule and sampling method as T054, label results **PRELIMINARY — NOT FINAL SC-009 EVIDENCE**, and obtain the provisional T059 owner assessment or pursue redesign or a separately approved governance route. Spike evidence does not complete final T054 or T057.
3. After a positive T059 assessment, obtain separate T060 approval before broader implementation. Complete any permitted remaining implementation, identify and verify the 8 GB target under T061, then recheck T053 where needed, run T054 on the final candidate, address T055 as applicable, and obtain the final T057 determination. Keep the design and acceptance gates blocked until their required final evidence and decisions exist.
4. Validate US1 independently with Pytest; do not claim success until the tests are actually run.

### Full assignment delivery

1. Complete dataset construction and preflight (Phase 6), schema/invariant validation (Phases 7–8), and deterministic per-attempt scoring (Phase 9).
2. Complete unified reports and harness (Phase 10), then human review/repair/reevaluation (Phase 11).
3. Complete Windows documentation, full verification, real evaluation, timing evidence, human approval, and traceability audit (Phase 12).
4. Preserve all initial, failure, repair, and final sanitized evidence. Keep every acceptance criterion fixed; if a criterion requires a legitimate governance change, pause and amend the specification before reevaluating.

## Notes

- Every listed task is pending. Task completion, test outcomes, evaluation scores, and human decisions must be recorded only after they occur.
- Contract schemas remain canonical in `specs/001-explain-ci-logs/contracts/`; implementation must not silently duplicate them.
- SQLite is not planned for the first release. No task may add cloud APIs, paid services, external AI, raw-log history, or automatic command execution.
