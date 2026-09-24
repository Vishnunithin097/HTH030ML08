# REST API Specification

## 1. Authentication & System Health
* `GET /health`
  * Status check returning `{"status": "ok"}`
* `POST /auth/login`
  * Body: `{"username": "admin", "password": "..."}`
  * Response: `{"access_token": "...", "token_type": "bearer"}`

---

## 2. Recommendation Services
* `GET /recommendations`
  * Query parameters:
    * `user_id`: Target user identifier (e.g. `999999999` for cold demo user)
    * `mode`: `pure` (ML-only) | `business_aware` (guardrail re-ranked)
    * `limit`: Number of items (default: 10)
  * Response: List of recommended item objects with scores, explainability badges, and guardrail statuses.
* `GET /recommendations/{item_id}/explain`
  * Detailed breakdown of why a specific item was ranked for the user.
* `GET /recommendations/{item_id}/counterfactual`
  * Sensitivity analysis (e.g., "How would recommendation rank change if inventory rose to 50 or margin dropped to 10%?").

---

## 3. Cold Start Simulation & Seed Services
* `POST /demo/cold-start/user`
  * Register a new synthetic shopper persona with category preferences.
* `POST /demo/cold-start/item`
  * Register a new un-interacted catalog item with description and price.

---

## 4. Business Guardrail Administration
* `GET /config/guardrails`
  * Returns active guardrail weights, margin floors, inventory thresholds.
* `PUT /config/guardrails`
  * (Requires Admin JWT) Updates active business guardrail parameters.

---

## 5. Metrics & Analytics
* `GET /metrics/ranking`: NDCG@10, Precision@10, Recall@10, MAP.
* `GET /metrics/business`: Total margin realized, inventory turn index, revenue lift.
* `GET /metrics/diversity`: Intra-list diversity, category coverage, catalog entropy.
