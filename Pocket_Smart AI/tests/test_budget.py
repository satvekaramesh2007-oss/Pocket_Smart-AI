from app.services.budget_service import (
    calculate_home_budget_breakdown,
    calculate_party_budget_breakdown,
    calculate_jewelry_budget_breakdown,
    evaluate_budget_status
)

def test_home_budget_breakdown():
    allocation = calculate_home_budget_breakdown(50000, ["Sofa", "Lights"])
    assert sum(allocation.values()) == 50000
    assert allocation["furniture"] == 24000.0

def test_budget_status_evaluation():
    status, rem = evaluate_budget_status(50000, 40000)
    assert status == "within_budget"
    assert rem == 10000

    status, rem = evaluate_budget_status(50000, 48000)
    assert status == "near_budget"

    status, rem = evaluate_budget_status(50000, 55000)
    assert status == "over_budget"
    assert rem == -5000
