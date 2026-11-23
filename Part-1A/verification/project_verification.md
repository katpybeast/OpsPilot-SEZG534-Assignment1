# Project verification summary

## Rule coverage
- active rule families: ci_cd, docker, kubernetes, security
- total active rules: 8
- covered deterministic tests: 8
- measured coverage: 100%
- verification source: tests/unit/test_security_rules.py and rule_registry.py

## Validation runtime
- benchmark: local validation of representative 1 MB CI/CD log and Kubernetes configuration samples
- measured runtime: under 5 seconds for both samples in the standard local Python environment
- verification source: tests/perf/test_validation_performance.py

## Offline determinism
- same input validated twice produced equivalent results without remote or network dependencies
- verification source: tests/unit/test_offline_determinism.py

## Architecture boundary check
- UI layer import boundaries are restricted to services and storage, not validation rules or raw validators
- verification source: tests/unit/test_architecture_boundaries.py

## Duplicate finding prevention
- final report security findings are deduplicated by rule_id within the canonical security family
- verification source: tests/unit/test_security_rules.py
