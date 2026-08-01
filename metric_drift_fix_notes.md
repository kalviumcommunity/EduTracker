# Why Manual Investigation is Necessary for Metric Drift

## Why not auto-fix?
- A validation script can detect divergence, but it cannot determine which side is correct.
- Auto-fixing based on a tolerance threshold risks normalizing incorrect data.
- A metric may drift due to a change in business logic, data source, or bug; an automated fix may hide the underlying issue.

## Risk of tolerance-based auto-fix
- It can mask creeping drift where both SQL and Python gradually move away from the intended definition.
- It may apply an incorrect correction when the difference is due to a data schema change or business rule update.
- Correctness requires human review, not just numeric agreement.

## Importance of manual review
- Ensures the root cause is understood and fixed.
- Verifies that the correct definition is being used for both layers.
- Prevents repeated regressions by documenting the intended logic.

## Recommended process
1. Detect drift with validation script.
2. Investigate the source of the discrepancy.
3. Correct the logic in the appropriate layer.
4. Re-run validation to confirm alignment.
5. Document the fix for future audits.
