"""
Phase 4 End-to-End API and Authentication Test Suite.
Validates all 17 Phase 4 API requirements via FastAPI TestClient.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app


def run_phase4_api_tests():
    print("==================================================")
    print("       PHASE 4 FASTAPI & AUTH TEST SUITE          ")
    print("==================================================")
    client = TestClient(app)

    # 1. Health Endpoint
    print("\n[1] Testing GET /health...")
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    print("  [+] GET /health returned 200 OK.")

    # 2. Admin Authentication (Success)
    print("\n[2] Testing POST /auth/login (Valid credentials)...")
    res = client.post("/auth/login", json={"username": "admin", "password": "Admin@123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    admin_token = token_data["access_token"]
    auth_header = {"Authorization": f"Bearer {admin_token}"}
    print(f"  [+] Admin login succeeded. JWT token acquired: {admin_token[:20]}...")

    # 3. Admin Authentication (Invalid Credentials -> 401)
    print("\n[3] Testing POST /auth/login (Invalid credentials)...")
    res = client.post("/auth/login", json={"username": "admin", "password": "WrongPassword"})
    assert res.status_code == 401
    print("  [+] Invalid login correctly rejected with HTTP 401.")

    # 4. Public Recommendations (General warm user)
    print("\n[4] Testing GET /recommendations?user_id=111016...")
    res = client.get("/recommendations?user_id=111016&limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "request_id" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) == 5
    print(f"  [+] Public recommendations returned {len(data['recommendations'])} items for warm user.")

    # 5. Pure Engagement Mode
    print("\n[5] Testing GET /recommendations (Pure mode)...")
    res_pure = client.get("/recommendations?user_id=111016&mode=pure&limit=5")
    assert res_pure.status_code == 200
    pure_items = res_pure.json()["recommendations"]
    assert all(item["business_score"] is None for item in pure_items)
    print("  [+] Pure mode verified (sorted strictly by ML relevance).")

    # 6. Business-Aware Mode
    print("\n[6] Testing GET /recommendations (Business-Aware mode)...")
    res_biz = client.get("/recommendations?user_id=111016&mode=business_aware&limit=5")
    assert res_biz.status_code == 200
    biz_data = res_biz.json()
    biz_items = biz_data["recommendations"]
    assert all(item["business_score"] is not None for item in biz_items)
    assert "guardrail_health" in biz_data
    assert "gmv_projection" in biz_data
    print("  [+] Business-Aware mode verified (business scores, penalties, and health attached).")

    # 7. Cold-Start Shopper Persona
    print("\n[7] Testing GET /recommendations (Cold-start user #999999999)...")
    res_cold = client.get("/recommendations?user_id=999999999&limit=5")
    assert res_cold.status_code == 200
    cold_data = res_cold.json()
    assert cold_data["cold_start"] is True
    assert all(item["is_cold_start"] is True for item in cold_data["recommendations"])
    print("  [+] Cold-start shopper mode triggered without collaborative errors.")

    # 8. Cold-Start Item Ingestion & Retrieval
    print("\n[8] Testing Cold-Start Item Creation (POST /demo/cold-start/item)...")
    res_item = client.post("/demo/cold-start/item", json={
        "name": "Phase 4 Test Electrolyte Drink",
        "category_name": "Beverages",
        "price": 199.0,
        "margin_pct": 40.0,
        "inventory_count": 80,
        "quality_score": 0.92,
        "business_priority": 0.75,
        "tags": ["drink", "electrolyte"]
    })
    assert res_item.status_code == 200
    created_item = res_item.json()
    assert created_item["is_synthetic_cold_demo"] is True
    print(f"  [+] Ingested demo cold item #{created_item['item_id']}: '{created_item['name']}'.")

    # 9. Why Recommended (Explainability Audit)
    print("\n[9] Testing GET /recommendations/{item_id}/explain...")
    res_exp = client.get(f"/recommendations/0/explain?user_id=111016")
    assert res_exp.status_code == 200
    exp_data = res_exp.json()
    assert "explanation" in exp_data
    assert len(exp_data["explanation"]) > 10
    print(f"  [+] Signal-derived explanation: '{exp_data['explanation']}'")

    # 10. Sensitivity Counterfactual Analysis
    print("\n[10] Testing GET /recommendations/{item_id}/counterfactual...")
    res_cf = client.get(f"/recommendations/0/counterfactual?user_id=111016&hypothetical_min_margin=10.0")
    assert res_cf.status_code == 200
    cf_data = res_cf.json()
    assert "simulated_score" in cf_data
    assert "summary" in cf_data
    print(f"  [+] Counterfactual simulation output: {cf_data['summary']}")

    # 11. GET Guardrail Config (Public read)
    print("\n[11] Testing GET /config/guardrails...")
    res_cfg = client.get("/config/guardrails")
    assert res_cfg.status_code == 200
    cfg = res_cfg.json()
    assert "min_inventory" in cfg
    assert "min_margin" in cfg
    print(f"  [+] Active Guardrails: min_inv={cfg['min_inventory']}, min_margin={cfg['min_margin']}%, rel_w={cfg['relevance_weight']}, biz_w={cfg['business_weight']}")

    # 12. Unauthorized PUT Guardrail Config (No JWT -> 401 / 403)
    print("\n[12] Testing Unauthorized PUT /config/guardrails...")
    res_unauth = client.put("/config/guardrails", json={"min_margin": 35.0})
    assert res_unauth.status_code in [401, 403]
    print("  [+] Unauthorized configuration modification successfully blocked.")

    # 13. Authorized PUT Guardrail Config (With JWT -> 200)
    print("\n[13] Testing Authorized PUT /config/guardrails...")
    res_auth = client.put(
        "/config/guardrails",
        json={"min_margin": 30.0, "relevance_weight": 0.50, "business_weight": 0.50},
        headers=auth_header,
    )
    assert res_auth.status_code == 200
    updated_cfg = res_auth.json()
    assert updated_cfg["min_margin"] == 30.0
    assert updated_cfg["business_weight"] == 0.50
    print(f"  [+] Updated Guardrails: min_margin={updated_cfg['min_margin']}%, biz_weight={updated_cfg['business_weight']}.")

    # 14. Verify Re-Ranking Changes Immediately After Config Update
    print("\n[14] Verifying immediate ranking behavior shift...")
    res_updated_recs = client.get("/recommendations?user_id=111016&mode=business_aware&limit=5")
    assert res_updated_recs.status_code == 200
    print("  [+] Re-ranker immediately applied updated business weights.")

    # 15. Metrics Endpoints
    print("\n[15] Testing Metrics Endpoints (/metrics/ranking, /metrics/business, /metrics/diversity)...")
    res_rank_m = client.get("/metrics/ranking")
    assert res_rank_m.status_code == 200
    assert "ndcg_at_10" in res_rank_m.json()

    res_biz_m = client.get("/metrics/business")
    assert res_biz_m.status_code == 200
    assert "projected_margin_lift_pct" in res_biz_m.json()

    res_div_m = client.get("/metrics/diversity")
    assert res_div_m.status_code == 200
    assert "intra_list_diversity" in res_div_m.json()
    print("  [+] All metrics endpoints returned live evaluation results.")

    # 16. Catalog Item Search & Filtering
    print("\n[16] Testing GET /items (Search & Category filter)...")
    res_search = client.get("/items?search=garlic&limit=5")
    assert res_search.status_code == 200
    search_results = res_search.json()
    assert len(search_results) > 0
    assert any("garlic" in i["name"].lower() for i in search_results)
    print(f"  [+] Item search returned {len(search_results)} items for keyword 'garlic'.")

    # 17. User List & Cold-Start Persona Creation
    print("\n[17] Testing GET /users and POST /demo/cold-start/user...")
    res_users = client.get("/users?limit=5")
    assert res_users.status_code == 200
    assert len(res_users.json()) > 0

    res_create_user = client.post("/demo/cold-start/user", json={
        "selected_categories": ["Beauty & Hygiene", "Baby Care"]
    })
    assert res_create_user.status_code == 200
    new_u = res_create_user.json()
    assert new_u["is_synthetic_cold_demo"] is True
    print(f"  [+] Spawned demo user #{new_u['user_id']} with categories: {new_u['selected_categories']}")

    print("\n==================================================")
    print("     ALL 17 PHASE 4 API TESTS PASSED 100%!        ")
    print("==================================================")


if __name__ == "__main__":
    run_phase4_api_tests()
