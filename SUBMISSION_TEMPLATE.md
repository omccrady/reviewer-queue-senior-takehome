# Submission

## Summary of changes
- Implemented state-aware review actions so the UI only offers valid next steps for each item.
- Tightened backend workflow rules so claim, approve, reject, and escalate only work for the expected statuses.
- Added clearer in-product guidance so reviewers can immediately see whether an item is claimable, in review, or already terminal.

## Bugs fixed
- Fixed the workflow so unassigned items can be claimed, in-review items can be resolved, and terminal items reject further actions with clear API errors.
- Prevented invalid state transitions from silently succeeding.

## Product/UX decisions
- The reviewer experience now surfaces the next best action instead of exposing all buttons equally.
- Action buttons are disabled when the selected item cannot use them, and a short status hint explains what the reviewer should do next.
- I kept the change scoped to the reviewer workflow rather than expanding into broader visual redesign.

## Tests added
- Added regression coverage for invalid transitions and terminal-state protection in the backend tests.

## Known gaps
- The current implementation uses a hardcoded reviewer identity of alex, matching the exercise constraints.
- The queue ordering remains the existing backend sort; I did not change the data model or add richer filtering beyond the workflow fix.

## Files changed and why
- backend/app/main.py: enforced workflow correctness and terminal-state protections.
- backend/tests/test_smoke.py: added targeted regression tests for invalid actions.
- frontend/src/App.vue: made action availability state-aware and surfaced helper text.
- frontend/src/styles.css: added lightweight guidance styling for the reviewer experience.

## AI assistance used
- Used AI for rapid implementation of the workflow rules, UI wiring, and test cases.
- Reviewed the generated changes against the exercise requirements before finalizing them.
