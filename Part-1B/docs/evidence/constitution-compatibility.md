# Constitution Compatibility and Measurement-Only Authorization

**Project**: OpsPilot AI — Intelligent DevOps Log Explainer  
**Recorded**: 2026-11-21  
**Decision scope**: Preliminary local model-runtime feasibility measurement only

## Owner authorization

The project owner authorizes a **preliminary, measurement-only local AI feasibility test** of the proposed Ollama runtime and `qwen2.5:1.5b` model on the documented Windows 8 GB computer.

If the exact proposed model is not already present locally, this decision authorizes downloading that model artifact for the preliminary measurement, subject to the project's free/local tooling, license-provenance, and data-safety requirements. It does **not** authorize installing Ollama or other software under the current request; separate installation authorization/procedure remains necessary if Ollama is absent.

## Explicit non-authorization and limitations

- This authorization does **not** establish constitutional compatibility with the requirement that the workflow fit an 8 GB Windows laptop and not require a large local model or other resource-intensive component.
- It does **not** establish that the model meets the 2 GiB SC-009 screen, the SC-005 latency target, or any quality/adequacy criterion. Those require actual measured evidence; no results are asserted here.
- Passing the 2 GiB numeric screen alone is not proof of the constitution's qualitative “not resource-intensive” requirement. The project owner must make a separate documented compatibility decision after reviewing evidence. If compatibility cannot be established, the architecture must be redesigned or a formal constitution amendment must be approved through governance.
- This decision does **not** change or amend the constitution.
- No application implementation, application run, full evaluation, or task completion is authorized by this decision.

## Gates

- The preliminary preflight in the current request is read-only and does not install software, download a model, start inference, or execute `Measure-Ollama.ps1`.
- If a requested read-only preflight check fails, stop and report the exact failure; do not attempt installation or model download.
- Any later model download or measurement must use the separately reviewed procedure, preserve sanitized provenance, and report SCREEN PASS/SCREEN FAIL/INCONCLUSIVE honestly. A preliminary measurement remains distinct from final app-plus-model acceptance.

## Owner authorization: T058 bounded preliminary spike

**Recorded**: 2026-11-22  
**Decision**: APPROVED — BOUNDED PRELIMINARY SPIKE

The project owner explicitly approves the bounded implementation-and-measurement spike on the current Windows development computer, reported to have 15.7 GiB of installed RAM. This computer is not the required 8 GB target.

- **Scope**: T001 baseline, T024 synthetic fixtures, the minimum runnable OpsPilot AI application, the real evaluator and model-access paths required for T053, provenance/no-pull/safety checks, preliminary combined application-plus-Ollama/model-runner measurement, and sanitized evidence.
- **Measurement**: Use the same three fixtures, model configuration, cold/warm schedule and sampling method as T054, retaining the ≤2 GiB threshold. Label all measurements **PRELIMINARY — NOT FINAL SC-009 EVIDENCE**.
- **Exclusions**: No broader implementation, final SC-009 acceptance, claim of 8 GB constitutional compatibility, or automatic completion of unrelated tasks. Each task remains subject to its own required work, evidence and permission.
- **Installation and provisioning**: Separate authorization is still required if needed.

## Owner authorization: T060 broader implementation

**Recorded**: 2026-11-23  
**Decision**: APPROVED — BROADER IMPLEMENTATION

The project owner explicitly approves broader implementation of the OpsPilot AI Part-1B application, evaluation harness, and integration of local Ollama runtime with Qwen2.5 1.5B model on the current Windows development computer (15.7 GiB RAM).

- **Scope**: Minimum complete, runnable end-to-end application implementation; real Streamlit UI; local model inference through Ollama; meaningful evaluation dataset (≥15 cases); evaluation pipeline with deterministic safety/validation steps, model generation, schema validation, scoring, and report generation; test coverage for new implementation.
- **Model inference requirement**: Model must genuinely generate explanations; deterministic fallbacks are not substitutes for AI inference and must not be counted as successful model output.
- **Failure handling**: If Ollama or model is unavailable or generates invalid output, application must report structured failure, not silently fall back to deterministic output.
- **Evidence retention**: Sanitized generated outputs, model provenance, response hashes, evaluation results, and failure evidence must be retained. No secrets or sensitive data included.
- **Resource evidence**: The current computer (15.7 GiB) is a development machine, not the required 8 GB target. Preliminary and final resource evidence remain clearly distinguished.

**Explicit non-authorization and limitations**:
- This approval does **NOT** establish 8 GB constitutional compatibility or satisfy the SC-009 ≤2 GiB resource requirement.
- It does **NOT** authorize complete final acceptance (T054), broader governance decisions (T061), related architectural changes (T055), or unrelated task completions (T057, T050).
- All measurements remain **PRELIMINARY — NOT FINAL SC-009 EVIDENCE**.
- Final acceptance requires separate demonstrated compliance on an actual 8 GB Windows target.

## Future decisions required

The T058 bounded spike and T060 broader implementation are approved as recorded above. T061 must identify and verify a genuine Windows 8 GB target before final T054 using sanitized system-generated evidence of its hardware, Windows version and installed RAM in bytes; a machine description alone is not sufficient. If no suitable target is available, final T054 and acceptance remain blocked unless a separately approved governance route resolves the applicable requirements. Neither preliminary measurement, broader implementation, nor authorization establishes constitutional compatibility or acceptance.

## References

- Governing constitution: `.specify/memory/constitution.md` (version 1.0.0; unchanged).
- Feature requirements and SC-009 protocol: `specs/001-explain-ci-logs/spec.md`.
- Proposed local model/resource design: `specs/001-explain-ci-logs/plan.md` and `specs/001-explain-ci-logs/research.md`.
- Measurement procedure: repository-root `Measure-Ollama.ps1` (not executed by this authorization record).
