# Research: OpsPilot AI — Intelligent DevOps Log Explainer

**Feature**: [spec.md](spec.md)  
**Date**: 2026-11-20

## Decisions

### Local application and model architecture

- **Decision**: Use one local Python application with Streamlit as the UI and Ollama on loopback as the inference runtime. The proposed initial model is `qwen2.5:1.5b`. For valid submissions, the model generates all eight response fields, grounds its explanatory claims in the sanitized log and deterministic evidence candidates, and selects evidence only from those candidates; independent code validates input/output, redacts sensitive values, constructs the prompt, enforces invariants, and scores results.
- **Rationale**: This introduces genuine stochastic model generation while keeping logs local and preserving independent safety/evaluation gates. Ollama provides a local Windows runtime and local HTTP API; no hosted inference is required.
- **Alternatives considered**: A deterministic rule engine alone does not demonstrate non-deterministic AI generation. Paid/hosted models violate requirements. A larger model increases memory risk without demonstrated need.

### Python and dependency baseline

- **Decision**: Target 64-bit Python 3.11+ on Windows. Use Streamlit and `jsonschema` as runtime Python dependencies, the standard library for local HTTP/JSON/redaction/evidence/report work, and Pytest/Ruff as development dependencies. Ollama is a separately installed local runtime. Audit direct/transitive dependency licenses and the exact model license/artifact provenance before acceptance.
- **Rationale**: The application dependencies are small; the model has its own separately measured memory cost. Ollama's public Qwen2.5 catalog lists the 1.5B artifact at about 986 MB and identifies Apache 2.0 licensing for this variant. Verify the pulled artifact's actual digest/license during setup rather than treating a family page as final artifact provenance.
- **Alternatives considered**: A custom JSON Schema implementation duplicates standards work. Transformers/PyTorch adds substantial package and RAM overhead for this scope. Paid/API SDKs and cloud endpoints are prohibited.

### Schema and validation layers

- **Decision**: Version JSON Schema documents using Draft 2020-12. Check the schema itself when initializing the validator; validate each response object with a prebuilt validator. Follow with independent structural, cross-field, evidence-grounding, redaction, and safety checks.
- **Rationale**: JSON Schema covers exact keys, types, enums, lengths, array bounds, and status-dependent field rules. Cross-field and input-relative requirements need a separate invariant layer and must not be conflated with rubric scores.
- **Alternatives considered**: Schema-only validation cannot prove evidence is present in input or that prompt-injection text was ignored. Semantic scoring is not an output-contract validator and cannot replace either layer.

### Strict serialization and parsing

- **Decision**: Construct the response as a native object, validate it independently, serialize once with strict non-finite-number rejection, and render that JSON text as the machine-readable result. Any JSON text accepted by the evaluation boundary must reject duplicate object keys and `NaN`/infinities.
- **Rationale**: Python's standard JSON module accepts duplicate property names and non-standard non-finite numbers by default; its documented hooks can reject these cases. `jsonschema` validates parsed instances, so parser strictness is a distinct concern.
- **Alternatives considered**: Relying on default parsing/serialization would fail the specification's duplicate-key and strict-JSON requirements. Returning only a UI-rendered object would not demonstrate the one-object JSON text contract.

### Local Streamlit operation

- **Decision**: Run Streamlit through loopback only (`127.0.0.1`), disable usage statistics, avoid external assets/URLs/telemetry and caches of submitted text, and permit only the local browser-to-Streamlit and app-to-Ollama (`127.0.0.1:11434`) HTTP connections at runtime.
- **Rationale**: Both UI and model are local. Project configuration can disable usage-stat collection and bind the local server. Disabling caching avoids unnecessary retention of sensitive submissions.
- **Alternatives considered**: Binding either service to all interfaces exposes it to the local network. Hosted deployment or non-loopback inference conflicts with the constitution and specification.

### Local environment and offline use

- **Decision**: Document a project-local `.venv` and a recreation workflow from declared dependencies. Runtime and evaluation must be offline. When setup must also be offline, use a Windows/Python-compatible local wheelhouse and pip's `--no-index` / `--find-links`; do not copy a virtual environment between machines.
- **Rationale**: Python documents virtual environments as non-portable and recommends recreating them. pip documents installing from local wheel directories without using an index. This separates initial dependency provisioning from the no-network runtime constraint.
- **Alternatives considered**: Checking in a virtual environment is brittle and platform-specific. Assuming a package index is reachable would make offline setup impossible; bundling an executable is outside the first-release scope.

### Local storage and evidence

- **Decision**: Do not add SQLite for the first release. Keep evaluation fixtures in versioned JSON and write sanitized, versioned evaluation reports as local JSON artifacts; never persist raw logs. Preserve earlier failure reports during repair instead of overwriting them.
- **Rationale**: The specified data volume and single-user workflow do not justify database operations. Immutable, sanitized files provide inspectable evidence and version control traceability with less complexity.
- **Alternatives considered**: SQLite is permitted but optional; it increases schema and migration work without a required query/history use case. Persisting raw inputs violates data-minimization principles.

### Stochastic local generation and provenance

- **Decision**: Use Ollama with proposed `qwen2.5:1.5b`, temperature `0.7`, no seed, `num_ctx` 4096, and `num_predict` 768 as initial test settings. For valid inputs, the model generates all eight response fields, grounds explanatory claims in candidate excerpts/sanitized log, and selects evidence only from candidates; deterministic extraction does not produce a successful fallback explanation. Record actual model tag/digest, Ollama version, loopback endpoint, effective settings, and each attempt's sanitized response artifact/hash.
- **Rationale**: Nonzero temperature with an omitted seed permits stochastic output; outputs can still coincide and no output diversity guarantee is made. Local inference avoids sending CI logs to a hosted model.
- **Alternatives considered**: A deterministic rule engine alone fails the assignment's non-deterministic AI requirement. A fixed seed/greedy decoding conflicts with stochastic generation. Larger models and GPU-heavy serving add risk without evidence they fit the 8 GB target.

### Licensing and local model installation

- **Decision**: Provision Ollama and the exact model artifact before offline operation, record their versions/digest/license source, then run inference only against `http://127.0.0.1:11434`. Disable model pulls/updates in the app. Dependencies/model installation may need prior provisioning or an offline wheelhouse; application runtime must not require internet.
- **Rationale**: Ollama documents native Windows support and a localhost API. Its public Qwen2.5 catalog lists the 1.5B variant at about 986 MB and states that variants other than 3B and 72B use Apache 2.0. The dependency/model audit must verify the exact artifact provenance and license in the installed environment.

### Windows, memory, and latency risks

- **Decision**: Use SC-009's exact fixtures and cold/warm protocol from `spec.md`; sample once per second the sum of working sets for unique PIDs in the Streamlit/Python application and Ollama/model-runner process trees. The conservative combined peak screen is ≤2 GiB. Record exact inputs, repetitions, cold/warm conditions, OS/hardware, model/runtime/digest, configuration, PID selection, sampling method, per-trial maxima, and overall peak in `docs/evidence/model-resource-acceptance.md`.
- **Latency target**: Separately assess SC-005 with the model already loaded: end-to-end from submission to schema-validated JSON, at least `ceil(0.95 × N)` of `N` valid fixtures in ≤5 seconds. Record cold model-load time separately in `reports/evaluations/performance.json`. Latency is independent of the 2 GiB screen.
- **Failure path**: Exceeding 2 GiB blocks overall acceptance. Document a smaller-model and/or quantization investigation, or obtain a justified specification revision through governance, then repeat the identical benchmark. Do not silently substitute deterministic rules or weaken either target.
- **Constitution stance**: The ≤2 GiB screen is a conservative measurable boundary, not a reinterpretation or proof of the constitution's qualitative “not resource-intensive” requirement. Qwen2.5 1.5B fit, quality, latency, and constitutional compatibility are unverified. A model artifact's disk size or a screen pass alone does not establish compatibility. The design/implementation gate is blocked until the project owner reviews actual evidence and records compatibility; otherwise redesign the architecture or obtain a separately approved formal constitution amendment. This plan does not amend the constitution.

### Evaluation and review

- **Decision**: Keep dataset preflight, three independent Ollama calls per case, output capture, schema validation, invariant/safety checks, semantic scoring, aggregate threshold decision, human decision, repair reference, and reevaluation as separate reported stages. Each attempt is worth 10 points; aggregate is `100 × total earned points / (30 × case_count)`. Preserve one sanitized response artifact/hash and model provenance per attempt. Require at least 15 cases, zero hard-gate failures, semantic aggregate ≥80%, then human approval.
- **Rationale**: This evaluates stochastic outputs without conflating generation with deterministic scoring. Schema/invariant failures cannot be offset by the aggregate, and the 80% threshold remains fixed.
- **Alternatives considered**: A single aggregate-only score can hide unsafe or malformed outputs. Automatic approval removes required human oversight. Adjusting the score after failures violates governance.

### Evaluation dataset coverage

- **Decision**: The minimum dataset is 15 unique synthetic cases, each run three times. Assign exactly one `primary_category` to each case, with at least two cases for each of the six categories. Require every primary category to appear in that case's expected response categories; when primary category is `UNKNOWN`, expect `UNKNOWN` and disable partial credit. Tags may overlap but collectively cover normal, boundary, ambiguous, underspecified, malformed, missing-information, and adversarial content. Each case stores exactly one expected confidence value and deterministic scoring predicates, not asserted results.
- **Rationale**: This implements the accepted category-coverage clarification while preventing category quotas from being satisfied by cases that do not evaluate that category, and respects the minimum size with multi-tag coverage.
- **Alternatives considered**: Counting a case under multiple primary categories obscures classification balance; requiring separate cases for each coverage tag would add unnecessary minimum cases when tags can overlap.

## Windows and 8 GB operating constraints
- Evaluate SC-005 as at least `ceil(0.95 × N)` of `N` valid fixed-dataset submissions returning schema-validated JSON within 5 seconds end-to-end with the model already loaded; record cold-load separately. SC-009's exact cold/warm workload screens peak working set at ≤2 GiB, but does not itself settle constitutional compatibility. Both are future acceptance checks, not measured results.

## Official references

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [JSON Schema validation specification](https://json-schema.org/draft/2020-12/json-schema-validation)
- [`jsonschema` validation and validator selection](https://python-jsonschema.readthedocs.io/en/stable/validate/)
- [Python JSON compliance, duplicate names, and non-finite numbers](https://docs.python.org/3/library/json.html#standard-compliance-and-interoperability)
- [Streamlit local app launch](https://docs.streamlit.io/develop/concepts/architecture/run-your-app)
- [Streamlit configuration and usage statistics](https://docs.streamlit.io/develop/concepts/configuration/options)
- [Python virtual environments, Windows activation, and portability](https://docs.python.org/3/library/venv.html)
- [pip local wheelhouse installation](https://pip.pypa.io/en/stable/user_guide/#installing-from-local-packages)
- [Pytest configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [Ruff configuration](https://docs.astral.sh/ruff/configuration/)
- [Ollama Windows documentation](https://docs.ollama.com/windows)
- [Ollama Generate API](https://docs.ollama.com/api/generate)
- [Ollama Qwen2.5 model catalog](https://ollama.com/library/qwen2.5)

## Unresolved implementation details for task planning

No specification-level ambiguity blocks design. The exact prompt wording, deterministic evidence-extraction criteria, synthetic case fixtures, and their literal expected markers are content to be authored during implementation and reviewed/versioned; this plan does not claim that cases have already been created or evaluated.
