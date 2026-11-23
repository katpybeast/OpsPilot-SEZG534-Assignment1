# OpsPilot AI — Intelligent DevOps Log Explainer Constitution

## Core Principles

### I. Specification-First Development
Every feature MUST begin with an agreed specification that defines user value, scope,
acceptance criteria, and failure behavior before implementation. Plans and tasks MUST trace
back to that specification; code changes MUST NOT silently redefine it. This keeps the
assignment reviewable and prevents implementation convenience from becoming the product
requirement.

### II. Local Windows Execution
The application and its required development, test, and evaluation workflows MUST run locally
on Windows. Core functionality MUST NOT depend on a hosted service or internet connection at
runtime. Setup instructions and acceptance checks MUST be reproducible on a Windows laptop.

### III. Free Tools; No Paid or Cloud Services
The project MUST use free tools and MUST NOT require paid APIs, paid model endpoints, or cloud
services. Any AI inference used by the application MUST run locally. Optional tools MUST NOT
become prerequisites for the required workflow. This constraint keeps costs at zero and data
under local control.

### IV. Data Minimization and Evidence Safety
Logs, prompts, outputs, evaluation fixtures, screenshots, and other evidence MUST NOT contain
secrets, credentials, personal data, or sensitive operational details. Inputs and evidence
MUST be sanitized before storage or sharing; accidental exposure MUST be reported and safely
redacted rather than copied into further artifacts. Retained evidence MUST be limited to what
is needed to demonstrate behavior and compliance.

### V. Strict Structured JSON Output
The machine-readable explanation response MUST be valid JSON conforming exactly to the
versioned output contract. Required fields, types, allowed values, and nullability MUST be
explicit. The response MUST NOT contain markdown fences, surrounding prose, undeclared fields,
or malformed/truncated JSON. Errors MUST be represented through a defined, machine-readable
failure contract rather than fabricated explanations.

### VI. Independent Schema and Invariant Validation
Generated JSON MUST be validated after generation by code independent of the generation step.
Validation MUST check both the declared schema and project invariants, including consistency,
required evidence references, and safety constraints where applicable. Invalid output MUST be
rejected or safely handled; a plausible-looking response MUST NOT bypass validation.

### VII. Deterministic Semantic Quality Evaluation
Explanation quality MUST be evaluated with a documented, deterministic rubric using explicit
criteria and reproducible scoring rules. The rubric MUST assess factual grounding in the input,
usefulness, uncertainty handling, and safe recommendations as applicable. A score MUST NOT be
treated as proof of correctness, and nondeterministic model-as-judge scoring MUST NOT be the
sole acceptance gate.

### VIII. Minimum Evaluation Dataset
The versioned JSON evaluation dataset MUST contain at least 15 distinct cases before the
evaluation acceptance gate can pass. Cases MUST cover representative ordinary failures,
ambiguous or insufficient evidence, malformed inputs, and adversarial content. Each case MUST
have expected checks that can be run reproducibly, and changes to cases or scoring MUST be
documented.

### IX. Prompt-Injection and Adversarial-Input Safety
Log content MUST be treated as untrusted data, never as instructions that override system
behavior, policy, output contracts, or the user's task. The application MUST test and defend
against prompt injection, instruction-like log text, malformed or oversized input, and attempts
to elicit secrets or unsafe actions. Explanations MUST distinguish observed log evidence from
inference and MUST NOT claim unsupported causes or execute suggested commands.

### X. Mandatory Human Review
Human review MUST remain mandatory after automated schema, invariant, and semantic evaluation.
Automation may identify issues or provide a score, but MUST NOT approve, deploy, or represent an
explanation as verified without a human review step. Reviewers MUST be able to inspect the
relevant sanitized input, output, and evaluation results.

### XI. Acceptance Criteria Are Immutable During Evaluation
Acceptance criteria and evaluation thresholds MUST be fixed before a candidate is evaluated.
They MUST NOT be weakened, selectively excluded, or redefined to obtain a passing result. If a
criterion is genuinely incorrect, change it through the documented specification and governance
process, explain the rationale, and rerun the complete affected evaluation.

### XII. Preserve the Development and Evaluation Record
The project MUST preserve the initial implementation state, meaningful failure results, repair
changes, and final evaluation evidence so the development path is auditable. Preserve source
history and sanitized, reproducible reports; do not retain raw sensitive data in order to
preserve evidence. Final results MUST identify the tested version, dataset, rubric, and outcome.

## Technology and Resource Constraints

- The implementation SHOULD use Python and Streamlit, with Pytest for automated tests and Ruff
  for linting and formatting checks. A deviation MUST have a documented scope or compatibility
  reason.
- Evaluation cases and expected checks MUST be stored in a human-readable JSON dataset.
- SQLite MAY be used when it materially helps local persistence; it MUST NOT be introduced when
	files or in-memory state meet the requirement more simply.
- Required workflows MUST be achievable on a Windows laptop with 8 GB RAM. The project MUST NOT
	require a large local model or other resource-intensive component to pass baseline acceptance.
- Dependencies MUST be free, locally installable, and limited to those needed for the defined
	scope. Setup and test commands MUST be documented for Windows.

## Development Workflow and Quality Gates

- Specifications MUST state measurable acceptance criteria, including JSON contract behavior,
  independent validation, safety cases, dataset size, rubric expectations, and human review.
- Tests MUST cover the JSON schema and invariants, input handling, adversarial cases, and
	evaluation rubric behavior. Pytest and Ruff MUST pass for a release candidate, with any
	exceptions explicitly recorded and justified.
- The full evaluation MUST run against the committed dataset and fixed rubric. Reports MUST
	include reproducible case-level outcomes and MUST preserve failures as well as passes.
- No release candidate may pass solely on aggregate scores: required safety, schema, invariant,
	and human-review gates are independently mandatory.
- Every change MUST be checked for local Windows compatibility, data exposure, and constitution
	compliance. Evidence MUST be sanitized before it enters the repository or is shared.

## Governance

This constitution is the governing source for project scope and quality gates. Specifications,
plans, tasks, implementation, and evaluation MUST comply with it. If a conflict is found, work
MUST pause at the affected gate until the conflict is resolved through an approved amendment or
the lower-level artifact is corrected.

Amendments MUST document their rationale, affected principles and artifacts, compatibility
impact, and any required re-evaluation. The project owner MUST approve amendments before they
are used to assess a candidate. Acceptance thresholds MUST NOT be changed retroactively to
convert a failure into a pass. Amendments MUST update the version and last-amended date in this
document.

Constitution versions use semantic versioning: MAJOR for incompatible governance changes or
removal/redefinition of a principle; MINOR for added principles or materially expanded
requirements; PATCH for clarifications and non-semantic wording changes. Compliance MUST be
reviewed during specification, planning, implementation, and final evaluation, with unresolved
violations recorded rather than waived silently.

**Version**: 1.0.0 | **Ratified**: 2026-11-15 | **Last Amended**: 2026-11-15
