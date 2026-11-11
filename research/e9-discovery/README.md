# E9: independent-domain discovery and input eligibility

**Selected next domain:** human MCF-10A optoFGFR/ERK signaling, Nałęcz-Jawecki et al., Zenodo 7808385 v1.1. Sources and acquisition-day splits are fixed before predictive evaluation. E9 outcome evaluation has not run.

Read [the substantive assessment and decision in Spanish](CIERRE_SUSTANTIVO_Y_DECISION_E9_ES.md), [source protocol](E9_SOURCE_PROTOCOL.json), [cohort manifest](E9_COHORT_MANIFEST.json) and [candidate registry](CANDIDATE_REGISTRY.json).

The discovery audit verified two complete CSV members (199,701 rows across two fields), recovered source schemas, mapped acquisition dates and inspected input records from the first exported trajectory in each of 15 interval files. No FD7/FD8 full-cycle pulse-event match was found within those inspected trajectories and integer slots of 1–30 minutes. Two independent scan implementations agree. This is an input eligibility result, not a direct cellular FD intervention result.

## Reproduce the bounded audit

Requires Python 3.11+ and `requests`. No GPU, MATLAB, simulation or biological outcome fitting is involved. Network access to Zenodo is required. HTTP byte ranges are checked before reading, with transfer budgets enforced; unsupported ranges fail explicitly instead of downloading a large archive.

```sh
python audit_public_sources.py
python audit_input_prefixes.py
python build_discovery_contract.py
```

`audit_public_sources.py` reads two complete small members and two header previews. `audit_input_prefixes.py` reads only the first track's input/timing fields in each interval CSV and retains that scope explicitly. `build_discovery_contract.py` independently checks matches using string searches and verifies that primary acquisition dates never cross splits. The pinned source metadata and inventory are included. Full archive digest verification remains required before E9 scoring.

`E9_SOURCE_PROTOCOL.json` fixes sources, eligibility, local evidence principles and day splits. A numerical evaluation protocol must still freeze models, horizons, early/late windows, support rules and guards before test scoring. Existing E6/E8 results and FD certificates remain unchanged.

See [data and code attribution](DATA_AND_CODE_ATTRIBUTION.md). Full papers, upstream datasets, manuscripts and confidential annexes are not part of this directory.
