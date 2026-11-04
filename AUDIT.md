# Repository audit — 4 November 2026

Source reviewed: `5fa846dc033d0a8d29e6e187ec876ae369f55616` on `main`. Changes are proposed on `audit/repository-improvements-2026-11-04`; nothing was merged or deployed.

## Changes

- Validate HTTP version syntax and permit valid extension-method tokens such as M-SEARCH.
- Count UTC timestamp overflow as an invalid log line instead of terminating analysis.
- Add regressions while preserving query redaction, subnet aggregation and escaped reports.

## Verification

9 automated behavioral tests passed. All 4 recorded source/test checks passed. Local verification used Node.js 26.12.0 and Python 3.15.0; CI should also confirm the configured deployment versions.

- `python -m unittest discover -s tests -v`
- `Python AST parse for source files`

Local HTML asset references were compared with the complete GitHub file inventory. Real desktop/mobile visual verification was blocked in this environment: the in-app preview could not reach the local server and the desktop browser did not expose a usable window. No claim of browser/device acceptance is made. Automated DOM/canvas simulations, where present, do not replace that check.

## Remaining limits and rollout

- No authentication or database. Log analysis stays local.
- Paths can still contain personal data; review generated reports before sharing.
