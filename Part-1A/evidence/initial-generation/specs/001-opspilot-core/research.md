# Research: OpsPilot Core

## Decision 1: Use deterministic rule-based validation instead of model-driven inference

**Decision**: Validation will rely on explicit rule sets for CI/CD logs, Dockerfiles, Kubernetes manifests, and security checks. Each rule will produce a normalized result with a rule ID, severity, description, and evidence.

**Rationale**: The constitution requires deterministic and explainable validation. A rule-based engine supports repeatability, easier test coverage, and clear evidence preservation without requiring cloud-based services or external APIs.

**Alternatives considered**: Model-based detection, heuristic regex-only detection, and dynamic external analysis. These were rejected because they are less explainable, less deterministic, and may require external infrastructure or untrusted processing.

## Decision 2: Keep validation local and offline

**Decision**: All analysis will run locally on the Windows machine using installed Python dependencies and SQLite. No cloud or remote API integration is part of the feature.

**Rationale**: The constitution explicitly forbids cloud infrastructure and external services. Local processing also reduces security risk by not sending uploaded content outside the user environment.

**Alternatives considered**: Cloud submission, remote rule evaluation, hosted dashboards. Rejected because they conflict with the local-first and zero-cost principles.

## Decision 3: Separate validation logic from UI and persistence

**Decision**: The project will have distinct modules for UI, validation rules, domain models, and SQLite persistence. Report generation and rule execution will be centralized and independently testable.

**Rationale**: The constitution requires modularity and testability. Separation also helps enforce consistent report schemas and easier maintenance for future rule additions.

**Alternatives considered**: Monolithic validation inside the dashboard code or single-file implementation. Rejected because that would overlap responsibilities and complicate testing.

## Decision 4: Use explicit PASS, FAIL, and WARNING output states

**Decision**: Each validation result will be normalized to one of three statuses, with mandatory issues never silently downgraded and warnings used only for non-critical risky conditions.

**Rationale**: The constitution mandates explicit result status semantics and prohibits silent downgrading of mandatory failures.

**Alternatives considered**: Binary pass/fail only or implicit warnings. Rejected because they reduce nuance and violate specification requirements.

## Decision 5: Enforce safe input handling before validation

**Decision**: Uploaded files will be validated for type, size, and basic readability. Files larger than 1 MB or unsupported content types will be rejected before analysis begins.

**Rationale**: The constitution requires untrusted input handling and explicit supported limits. This reduces the likelihood of resource exhaustion or unsafe processing.

**Alternatives considered**: Accepting all file types and sizes. Rejected because it violates the defined 1 MB constraint and increases risk.

## Notes

- No technical clarification blockers remain from the feature specification.
- No external API or cloud integration is necessary for the initial feature release.
- The main design risk is maintaining deterministic, explainable findings across multiple rule families while preserving consistent evidence formatting.
