"""
B2, part 2 — implement the cost-tagging check.

Read fixtures/plan.json for the shape of a `terraform show -json` plan: a `resource_changes`
list, where each entry has a `type`, an `address`, and `change.after.tags`.

Implement check_plan() so it:
  - Looks at every resource being created or updated (skip anything whose change.actions
    isn't "create" or "update" — a "no-op"/"read" change, or a "delete" with no `after`
    block at all).
  - Fails (returns a non-zero exit code) if the resource is missing the tag that identifies
    the real billing unit, per README.md's domain model — not whatever tag the resource
    happens to already carry.
  - Is idempotent: running this twice against the same plan file produces the same result,
    with no duplicate output and no flipped pass/fail. This is about a single run being
    stable and repeatable — it does not require remembering anything between runs.
  - Prints which specific resource address(es) are missing the tag.

Run manually: python scripts/cost_tag_check.py fixtures/plan.json
"""
import json
import sys


def check_plan(plan_path: str) -> int:
    """
    Returns an exit code: 0 if every resource being created or updated has
    `landlord_account_id`, non-zero otherwise.
    """
    with open(plan_path, encoding="utf-8") as fh:
        plan = json.load(fh)

    REQUIRED_TAG = "landlord_account_id"
    ACTIONABLE = {"create", "update"}

    # Collect violations: resource addresses missing the required billing tag.
    # Using `address` as the dedup key within a single run — Terraform guarantees
    # each address is unique in a plan, so iterating resource_changes never
    # produces the same address twice.  That is what gives this function its
    # idempotency: the plan file is the sole source of truth, no external state
    # is written or read between invocations, and each address appears at most
    # once per run.
    violations = []
    seen = set()  # guard against a malformed plan that repeats an address
    for resource in plan.get("resource_changes", []):
        address = resource["address"]
        if address in seen:
            continue
        seen.add(address)

        actions = set(resource.get("change", {}).get("actions", []))
        if not actions & ACTIONABLE:
            continue

        after = resource.get("change", {}).get("after") or {}
        tags = after.get("tags") or {}
        if REQUIRED_TAG not in tags:
            violations.append(address)

    if violations:
        for addr in violations:
            print(f"MISSING TAG '{REQUIRED_TAG}': {addr}")
        return 1

    print(f"All create/update resources carry '{REQUIRED_TAG}' — OK")
    return 0


if __name__ == "__main__":
    sys.exit(check_plan(sys.argv[1]))
