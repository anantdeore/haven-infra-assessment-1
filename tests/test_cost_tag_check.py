"""
Write tests here proving:
  1. Happy path: running the check against fixtures/plan.json correctly flags the resources
     missing `landlord_account_id` (listing_media, mls_feed_sync) and passes the ones that
     have it (landlord_media[0], screening_report_export). The fixture also has a "no-op"
     entry and a "delete" entry with no `after` block at all — neither should appear in the
     output or crash the check.
  2. Idempotency: running the check twice against the same plan file produces the same
     result both times, with no duplicated output.

check_plan() takes a file path, not a dict — for a case that needs its own plan contents
instead of the shared fixture, write one with pytest's `tmp_path` rather than editing
fixtures/plan.json. You don't need to shell out to the real script for every case.
"""
from scripts.cost_tag_check import check_plan

FIXTURE_PLAN = "fixtures/plan.json"

# Resources in fixtures/plan.json that are create/update but MISSING landlord_account_id:
#   - aws_s3_bucket.listing_media  (has only tenant_id)
#   - aws_lambda_function.mls_feed_sync  (has empty tags)
# Resources that correctly carry landlord_account_id:
#   - aws_s3_bucket.landlord_media[0]
#   - aws_lambda_function.screening_report_export
# Resources that must be silently skipped:
#   - aws_s3_bucket.archive_media  (no-op)
#   - aws_s3_bucket.decommissioned_media  (delete with no `after`)


def test_flags_missing_and_passes_present(capsys):
    exit_code = check_plan(FIXTURE_PLAN)

    assert exit_code != 0, "Plan has resources missing landlord_account_id — must fail"

    captured = capsys.readouterr()
    out = captured.out

    # Violations must be reported
    assert "aws_s3_bucket.listing_media" in out
    assert "aws_lambda_function.mls_feed_sync" in out

    # Correctly tagged resources must NOT be reported as violations
    assert "aws_s3_bucket.landlord_media" not in out or "MISSING" not in out.split("aws_s3_bucket.landlord_media")[0]
    assert "aws_lambda_function.screening_report_export" not in out or (
        "MISSING TAG" not in out.split("aws_lambda_function.screening_report_export")[0]
    )

    # Skipped resources must not appear at all
    assert "aws_s3_bucket.archive_media" not in out
    assert "aws_s3_bucket.decommissioned_media" not in out


def test_idempotent_same_exit_code_and_output(capsys):
    """Running check_plan twice on the same plan file must produce the same exit code
    and identical stdout — no duplicated lines, no flipped result."""
    exit_code_1 = check_plan(FIXTURE_PLAN)
    out_1 = capsys.readouterr().out

    exit_code_2 = check_plan(FIXTURE_PLAN)
    out_2 = capsys.readouterr().out

    assert exit_code_1 == exit_code_2, "Exit code must be stable across repeated runs"
    assert out_1 == out_2, "Output must be identical across repeated runs (no duplicates)"


def test_all_tagged_plan_passes(tmp_path):
    """A plan where every create/update resource carries landlord_account_id returns 0."""
    plan = {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.foo",
                "type": "aws_s3_bucket",
                "name": "foo",
                "change": {
                    "actions": ["create"],
                    "after": {"tags": {"landlord_account_id": "la-001"}},
                },
            },
            {
                "address": "aws_lambda_function.bar",
                "type": "aws_lambda_function",
                "name": "bar",
                "change": {
                    "actions": ["update"],
                    "after": {"tags": {"landlord_account_id": "la-002"}},
                },
            },
        ]
    }
    import json

    plan_file = tmp_path / "good_plan.json"
    plan_file.write_text(json.dumps(plan))

    assert check_plan(str(plan_file)) == 0


def test_noop_and_delete_skipped(tmp_path):
    """no-op and delete actions are silently ignored even when missing the tag."""
    import json

    plan = {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.noop_res",
                "type": "aws_s3_bucket",
                "name": "noop_res",
                "change": {"actions": ["no-op"], "after": {"tags": {}}},
            },
            {
                "address": "aws_s3_bucket.deleted_res",
                "type": "aws_s3_bucket",
                "name": "deleted_res",
                "change": {"actions": ["delete"], "after": None},
            },
        ]
    }
    plan_file = tmp_path / "skip_plan.json"
    plan_file.write_text(json.dumps(plan))

    assert check_plan(str(plan_file)) == 0
