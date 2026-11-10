"""
Write tests here proving:
  1. A PropertyManager scoped to la-001 (pm-001) is DENIED access to la-002's tenant's
     screening report (rep-002).
  2. The same PropertyManager (pm-001) IS allowed access to their own account's screening
     report (rep-001).

Use the `property_managers`, `properties`, `tenants`, and `screening_reports` fixtures from
conftest.py — don't re-invent the seed data here.
"""
from app.access_control import can_access_screening_report


def test_cross_account_denied(property_managers, properties, tenants, screening_reports):
    """pm-001 (la-001) must NOT see rep-002 which belongs to la-002's tenant."""
    pm_001 = next(pm for pm in property_managers if pm.id == "pm-001")
    rep_002 = next(r for r in screening_reports if r.id == "rep-002")

    result = can_access_screening_report(
        pm_001, rep_002, properties=properties, tenants=tenants
    )
    assert result is False, "Cross-account access must be denied"


def test_same_account_allowed(property_managers, properties, tenants, screening_reports):
    """pm-001 (la-001) MUST see rep-001 which belongs to la-001's tenant."""
    pm_001 = next(pm for pm in property_managers if pm.id == "pm-001")
    rep_001 = next(r for r in screening_reports if r.id == "rep-001")

    result = can_access_screening_report(
        pm_001, rep_001, properties=properties, tenants=tenants
    )
    assert result is True, "Same-account access must be allowed"
