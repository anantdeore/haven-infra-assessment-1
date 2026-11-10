# Design Notes

## B2 — idempotency key

State exactly what key your `cost_tag_check.py` uses to decide whether two resources in the
same run are "the same" for dedup purposes, and why running it twice against an unchanged
plan file produces identical output and exit code without the script keeping any record
between runs. Use the word "idempotency" in your explanation.

The key used to determine whether two resource entries in a single run are "the same"
is the `address` field emitted by `terraform show -json`. Each Terraform plan guarantees
that every `address` in `resource_changes` is unique, so iterating the list once and
writing each address into a `seen` set is sufficient to process every resource exactly
once per invocation. This is what gives `check_plan` its **idempotency**: the function
has no side-effects and writes no state between calls — it reads the same static plan
file and produces the same set of violations every time. Running it twice on an unchanged
plan file yields the same exit code and the same stdout output because the only input is
the file itself, and `address` uniqueness within the plan means no resource can appear in
the output more than once per run.

## Any other decision with a non-obvious alternative

**Access check walks the full chain, not a shortcut.**
`ScreeningReport` only carries `tenant_id`. An earlier version of the code might be
tempted to compare `tenant_id` values directly, but `tenant_id` is not the billing
boundary — `landlord_account_id` is (per the README). The correct predicate is
`actor.landlord_account_id == property.landlord_account_id`, reached by traversing
`report → tenant → property`. Fail-closed: any missing link returns `False`.

**`landlord_account_id` tag, not `tenant_id`.**
`fixtures/plan.json` already contains `tenant_id` on some resources. The README warns
explicitly that the existing tagging "reflects how it was built, not a spec to replicate."
The required tag for cost attribution is `landlord_account_id` — the real billing unit.
