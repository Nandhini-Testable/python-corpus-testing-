"""Exercises planted fixtures and microservices code for coverage / branch metrics.

These tests intentionally call analysis helpers that other suites avoid so
Coverage.py sees more branches without deleting the planted defect fixtures.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for extra in (
    os.path.join(ROOT, "packages", "contracts", "src"),
    os.path.join(ROOT, "services", "gateway_service", "src"),
    os.path.join(ROOT, "services", "order_service", "src"),
    os.path.join(ROOT, "services", "pricing_service", "src"),
):
    if extra not in sys.path:
        sys.path.insert(0, extra)

from orderlab.analysis import complexity_sample, taint_fixture  # noqa: E402
from orderlab.analysis.ferpa_pii_fixture import (  # noqa: E402
    COPPA_GUARDIAN_PHONE,
    FERPA_EMAIL_SAMPLE,
    STUDENT_RECORDS,
)
from orderlab.analysis.sast_fixture import (  # noqa: E402
    evaluate_rule,
    legacy_checksum,
    load_settings,
    run_report,
)
from orderlab import __main__ as orderlab_main  # noqa: E402


@pytest.mark.parametrize(
    "weight,region,hazardous,express,tier,zone,promo,expect_sub",
    [
        (0, "US", False, False, "gold", 1, None, "invalid"),
        (5, "EU", True, False, "gold", 1, None, "haz-light-eu"),
        (31, "EU", True, False, "gold", 1, None, "haz-heavy-eu"),
        (8, "US", True, False, "gold", 8, None, "haz-remote-us"),
        (21, "US", True, False, "gold", 1, None, "haz-heavy-us"),
        (8, "US", True, False, "gold", 1, None, "haz-std-us"),
        (20, "APAC", True, False, "gold", 1, None, "haz-intl"),
        (3, "US", False, True, "gold", 1, None, "express-us"),
        (3, "US", False, True, "silver", 1, None, "express-us"),
        (3, "US", False, True, "standard", 1, None, "express-us"),
        (60, "US", False, False, "gold", 1, None, "freight"),
        (15, "US", False, False, "gold", 1, None, "parcel-heavy"),
        (2, "US", False, False, "gold", 1, None, "parcel"),
        (5, "EU", False, True, "gold", 1, "FREESHIP", "express-eu"),
    ],
)
def test_classify_shipment_branches(
    weight, region, hazardous, express, tier, zone, promo, expect_sub,
):
    order = object()
    row = complexity_sample.classify_shipment(
        order, region, tier, weight, hazardous, express, 50.0, zone, promo,
    )
    assert expect_sub in row["band"]


def test_summarise_bands_minimum_filter():
    rows = [
        {"band": "a", "surcharge": 1.0},
        {"band": "b", "surcharge": 10.0},
    ]
    assert complexity_sample.summarise_bands(rows, minimum=5.0) == {"b": 10.0}


def test_sast_fixture_smoke():
    assert legacy_checksum("payload") != ""
    with pytest.raises(TypeError):
        load_settings("key: value\n")  # unsafe loader intentionally omitted
    with pytest.raises(Exception):
        run_report("missing-report-404")
    assert evaluate_rule("1 + 1", {}) == 2


def test_taint_sanitised_lookup():
    class _Cursor:
        def __init__(self):
            self.sql = None
            self.params = None

        def execute(self, sql, params=()):
            self.sql = sql
            self.params = params
            return None

        def fetchall(self):
            return []

    cur = _Cursor()
    taint_fixture.sanitised_lookup(cur, "O-1")
    assert "?" in cur.sql


def test_ferpa_strings_are_present():
    assert "@" in FERPA_EMAIL_SAMPLE
    assert len(STUDENT_RECORDS) >= 2
    assert COPPA_GUARDIAN_PHONE.startswith("+")


def test_main_cli_json(capsys):
    rc = orderlab_main.main([])
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert rc in (0, 2)
    assert "priced" in doc


def test_gateway_service_paths(gold_order):
    from gateway_service import handle, health

    bad = handle({"version": "1.0", "batch_id": "B-1", "orders": []})
    assert isinstance(bad, dict)

    good = handle({
        "version": "1.0",
        "batch_id": "B-2",
        "orders": [{
            "order_id": gold_order.order_id,
            "channel": gold_order.channel,
            "region": gold_order.region,
            "tier": gold_order.tier,
            "lines": [
                {
                    "sku": line.sku,
                    "quantity": line.quantity,
                    "unit_price": line.unit_price,
                }
                for line in gold_order.lines
            ],
        }],
    })
    assert good["batch_id"] == "B-2"
    assert len(good["results"]) == 1
    assert health()["service"] == "gateway-service"