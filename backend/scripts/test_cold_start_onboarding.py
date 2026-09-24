"""
Verification Test Suite for Cold-Start Onboarding Interests Driving Recommendations.
Tests end-to-end flows for multi-category declarations, custom categories,
recommendation differentiation, business guardrail re-ranking, and explainability veracity.
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"


def make_request(endpoint: str, method: str = "GET", payload: dict = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_cold_start_flows():
    print("=" * 70)
    print("RUNNING COLD-START ONBOARDING INTEGRATION TEST SUITE")
    print("=" * 70)
    passed = 0
    total = 5

    # -------------------------------------------------------------
    # TEST SCENARIO 1: Multi-category ['Beauty & Hygiene', 'Gourmet & World Food']
    # -------------------------------------------------------------
    try:
        cats_1 = ["Beauty & Hygiene", "Gourmet & World Food"]
        user_res_1 = make_request("/demo/cold-start/user", method="POST", payload={"selected_categories": cats_1})
        uid_1 = user_res_1["user_id"]

        assert user_res_1["is_cold_start"] is True or user_res_1["is_synthetic_cold_demo"] is True
        assert user_res_1["interaction_count"] == 0
        assert user_res_1["selected_categories"] == cats_1, f"Expected {cats_1}, got {user_res_1['selected_categories']}"

        recos_1 = make_request(f"/recommendations?user_id={uid_1}&mode=business_aware&limit=12")
        assert recos_1["cold_start"] is True
        assert recos_1["interaction_count"] == 0
        assert recos_1["selected_categories"] == cats_1
        assert len(recos_1["recommendations"]) > 0

        # Check category representation
        reco_cats_1 = [r["category_name"] for r in recos_1["recommendations"]]
        has_beauty = any("Beauty" in c for c in reco_cats_1)
        has_gourmet = any("Gourmet" in c for c in reco_cats_1)
        assert has_beauty or has_gourmet, f"Recommendations must reflect selected categories: {reco_cats_1}"
        
        # Verify explainability veracity (no fake purchase claims)
        for r in recos_1["recommendations"]:
            assert "frequently bought" not in r["explanation"].lower()
            assert "previous" not in r["explanation"].lower()

        print(f"[PASS] Scenario 1: Multi-category cold shopper #{uid_1} created with {cats_1}.")
        print(f"       -> Recommendations received ({len(recos_1['recommendations'])} items). Sample categories: {set(reco_cats_1)}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Scenario 1: {e}")

    # -------------------------------------------------------------
    # TEST SCENARIO 2: Multi-category ['Beverages', 'Snacks & Branded Foods']
    # -------------------------------------------------------------
    try:
        cats_2 = ["Beverages", "Snacks & Branded Foods"]
        user_res_2 = make_request("/demo/cold-start/user", method="POST", payload={"selected_categories": cats_2})
        uid_2 = user_res_2["user_id"]

        assert user_res_2["selected_categories"] == cats_2
        recos_2 = make_request(f"/recommendations?user_id={uid_2}&mode=business_aware&limit=12")
        assert recos_2["selected_categories"] == cats_2

        reco_cats_2 = [r["category_name"] for r in recos_2["recommendations"]]
        has_bev_or_snack = any("Beverages" in c or "Snacks" in c for c in reco_cats_2)
        assert has_bev_or_snack, f"Expected Beverages or Snacks in {reco_cats_2}"

        # Distinct slates between user 1 and user 2
        items_1 = {r["item_id"] for r in recos_1["recommendations"]}
        items_2 = {r["item_id"] for r in recos_2["recommendations"]}
        assert items_1 != items_2, "Recommendations must dynamically change when onboarding categories differ!"

        print(f"[PASS] Scenario 2: Beverages + Snacks cold shopper #{uid_2} created with {cats_2}.")
        print(f"       -> Slate distinct from Scenario 1. Sample categories: {set(reco_cats_2)}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Scenario 2: {e}")

    # -------------------------------------------------------------
    # TEST SCENARIO 3: Single-category ['Beauty & Hygiene']
    # -------------------------------------------------------------
    try:
        cats_3 = ["Beauty & Hygiene"]
        user_res_3 = make_request("/demo/cold-start/user", method="POST", payload={"selected_categories": cats_3})
        uid_3 = user_res_3["user_id"]

        assert user_res_3["selected_categories"] == ["Beauty & Hygiene"]
        recos_3 = make_request(f"/recommendations?user_id={uid_3}&mode=business_aware&limit=12")
        assert recos_3["selected_categories"] == ["Beauty & Hygiene"]

        reco_cats_3 = [r["category_name"] for r in recos_3["recommendations"]]
        beauty_count = sum(1 for c in reco_cats_3 if "Beauty" in c)
        assert beauty_count >= len(reco_cats_3) // 2, f"Expected predominantly Beauty & Hygiene, got: {reco_cats_3}"

        print(f"[PASS] Scenario 3: Single-category cold shopper #{uid_3} strictly preserved as ['Beauty & Hygiene'].")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Scenario 3: {e}")

    # -------------------------------------------------------------
    # TEST SCENARIO 4: Custom Category ['Beauty & Hygiene', 'Organic Personal Care']
    # -------------------------------------------------------------
    try:
        cats_4 = ["Beauty & Hygiene", "Organic Personal Care"]
        user_res_4 = make_request("/demo/cold-start/user", method="POST", payload={"selected_categories": cats_4})
        uid_4 = user_res_4["user_id"]

        assert user_res_4["selected_categories"] == cats_4
        recos_4 = make_request(f"/recommendations?user_id={uid_4}&mode=business_aware&limit=12")
        assert recos_4["selected_categories"] == cats_4
        assert len(recos_4["recommendations"]) == 12

        print(f"[PASS] Scenario 4: Custom category preserved in list {cats_4} without runtime failure.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Scenario 4: {e}")

    # -------------------------------------------------------------
    # TEST SCENARIO 5: Pure Relevance vs Business-Aware on Cold-Start Slate
    # -------------------------------------------------------------
    try:
        pure_recs = make_request(f"/recommendations?user_id={uid_1}&mode=pure&limit=8")
        biz_recs = make_request(f"/recommendations?user_id={uid_1}&mode=business_aware&limit=8")

        for p in pure_recs["recommendations"]:
            assert p["final_score"] == p["relevance_score"], f"In pure mode final_score ({p['final_score']}) must equal relevance ({p['relevance_score']})"

        assert biz_recs["gmv_projection"] is not None
        assert biz_recs["guardrail_health"] is not None

        print(f"[PASS] Scenario 5: Pure mode strictly preserves relevance; Business-Aware mode applies commercial guardrails.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Scenario 5: {e}")

    print("=" * 70)
    print(f"TEST RESULTS: {passed}/{total} SCENARIOS PASSED")
    print("=" * 70)
    if passed == total:
        print("[SUCCESS] All Cold-Start Onboarding Acceptance Tests Passed!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    test_cold_start_flows()
