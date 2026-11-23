# Preliminary local model-runtime resource measurement

## Scope and machine

This is a preliminary model-runtime-only test, not final application-plus-model
SC-009 validation or acceptance. The application was not included. The observed
sample maxima are below 2 GiB, but 8 GB compatibility and constitutional
compliance remain unproven and require the separate prescribed assessment.

- Machine details supplied for this summary: Windows 11, 15.73 GiB installed RAM.
  The CSVs do not independently record the OS version or installed RAM.
- Model recorded in every CSV: `qwen2.5:1.5b` (Qwen2.5 1.5B).
- Exact recorded model digest:
  `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`.
- Observed installed Ollama version: `0.40.17`, as shown by earlier terminal
  output and recorded in all six CSVs. The separately supplied `0.4.17` value
  conflicts with that terminal and CSV evidence.

## Method and interpretation

The probe sampled the unique PIDs in the PowerShell controller/job and local
Ollama server/model-runner process trees, summing their working sets. Sampling
was intended at approximately one-second intervals; collection overhead makes
the recorded intervals longer. A call maximum below is the maximum observed
`SAMPLE_TOTAL` across its pre-job, job-start, inference and post-call phases,
not a guaranteed true peak. Sampling can miss transient peaks.

Gap values are the maximum recorded `GapSeconds` within each call, rounded in
the CSV to three decimal places. Gap detection resets for each call and does
not cover idle time between calls. Minimum free memory is the lowest
`FreePhysicalBytes` among that call's samples, not the minimum for the entire
machine session. Values in the tables are bytes, not GiB.

A `post-call` sample is written after the probe receives a completed response;
it provides evidence of inference completion, not a record of response content
or a validated quality result. The CSVs do not record console completion
messages or inference durations.

## Cold results

Each row is one selected fixture's model-cold call. All three have a post-call
sample and no flagged gap over two seconds.

| Fixture | Maximum sampled working set (bytes) | Minimum sampled free memory (bytes) | Maximum gap (s) | Completion |
|---|---:|---:|---:|---|
| `resource-build-001` | 1,295,208,448 | 2,528,337,920 | 1.320 | Post-call recorded |
| `resource-dependency-001` | 964,214,784 | 2,818,596,864 | 1.246 | Post-call recorded |
| `resource-test-001` | 952,643,584 | 2,813,485,056 | 1.232 | Post-call recorded |

The largest observed sampled working set in these completed cold calls was
1,295,208,448 bytes (1.206257 GiB); their lowest observed free memory was
2,528,337,920 bytes (2.354698 GiB), both in the build call.

## Warm results

The warm CSV records one completed warm-up per fixture, followed by three
completed measured repetitions per fixture. Each call below has a post-call
sample and no flagged gap over two seconds.

| Fixture | Warm-up maximum (bytes) | Minimum sampled free memory (bytes) | Maximum gap (s) |
|---|---:|---:|---:|
| `resource-build-001` | 1,017,106,432 | 3,642,851,328 | 1.200 |
| `resource-dependency-001` | 1,013,432,320 | 3,693,412,352 | 1.205 |
| `resource-test-001` | 1,028,743,168 | 3,676,975,104 | 1.240 |

| Repetition | Fixture | Maximum sampled working set (bytes) | Minimum sampled free memory (bytes) | Maximum gap (s) |
|---:|---|---:|---:|---:|
| 1 | `resource-build-001` | 1,062,031,360 | 3,688,321,024 | 1.225 |
| 1 | `resource-dependency-001` | 1,026,895,872 | 3,725,402,112 | 1.215 |
| 1 | `resource-test-001` | 1,021,353,984 | 3,758,108,672 | 1.200 |
| 2 | `resource-build-001` | 1,043,374,080 | 3,474,722,816 | 1.226 |
| 2 | `resource-dependency-001` | 1,055,334,400 | 3,454,218,240 | 1.248 |
| 2 | `resource-test-001` | 1,019,944,960 | 3,632,295,936 | 1.248 |
| 3 | `resource-build-001` | 1,018,601,472 | 3,613,544,448 | 1.227 |
| 3 | `resource-dependency-001` | 1,021,255,680 | 3,630,137,344 | 1.286 |
| 3 | `resource-test-001` | 1,026,899,968 | 3,668,189,184 | 1.218 |

Across all 12 warm calls, the maximum sampled working set was 1,062,031,360
bytes (0.989094 GiB), the minimum sampled free memory was 3,454,218,240 bytes
(3.216991 GiB), and the largest recorded within-call gap was 1.286 seconds.
Across the completed cold and warm evidence, no sample is flagged as having a
gap over two seconds. The overall observed maximum and minimum free memory
are the cold-build values above.

## Earlier incomplete or inconclusive evidence

- **ColdTest01** (`resource-test-001`): the CSV ends during `model-cold-load`
  without a post-call sample. No identifiable model-runner row was recorded
  before it ended. The CSV contains no error or stop reason, so the cause and
  whether inference completed cannot be determined from it. Its incomplete
  samples are not substituted for the completed ColdTest02 result.
- **WarmAll02**: the reported error was `INCONCLUSIVE: PowerShell
  background-job PID is missing from the measured process trees.` The CSV
  records three completed warm-ups, three completed measured calls, and samples
  for `resource-build-001` in `warm-measured-2`, with no post-call for that
  call. A job-host exit between a job-state check and the snapshot is a likely
  race; the failing snapshot was not written, so the precise cause is not
  established by the CSV. This incomplete attempt is not substituted for
  WarmAll03.

These are the earlier incomplete or inconclusive attempts represented by the
available preliminary CSVs. The CSVs do not establish whether other attempts
without saved CSVs occurred.

## Evidence CSVs

- Completed cold build: [docs/evidence/model-resource-preliminary-cold-build-01.csv](./model-resource-preliminary-cold-build-01.csv)
- Completed cold dependency: [docs/evidence/model-resource-preliminary-cold-dependency-01.csv](./model-resource-preliminary-cold-dependency-01.csv)
- Earlier incomplete cold test: [docs/evidence/model-resource-preliminary-cold-test-01.csv](./model-resource-preliminary-cold-test-01.csv)
- Completed cold test: [docs/evidence/model-resource-preliminary-cold-test-02.csv](./model-resource-preliminary-cold-test-02.csv)
- Earlier inconclusive warm attempt: [docs/evidence/model-resource-preliminary-warm-02.csv](./model-resource-preliminary-warm-02.csv)
- Completed warm schedule: [docs/evidence/model-resource-preliminary-warm-03.csv](./model-resource-preliminary-warm-03.csv)
