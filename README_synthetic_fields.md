# Notice on Synthetic Business Fields

## Purpose and Scope
The underlying public datasets (**RetailRocket** and **BigBasket**) contain implicit interaction logs and catalog product metadata, but do not contain live internal enterprise ERP fields such as real-time warehouse inventory counts, commercial profit margins, or internal quality ratings.

To evaluate business guardrails and multi-objective re-ranking in a realistic e-commerce setting, this project supplements product catalog items with synthetic business metadata.

---

## Field Specifications

| Field Name | Type | Range / Constraints | Generation Rationale / Behavior |
| :--- | :--- | :--- | :--- |
| `margin_pct` | `NUMERIC(5,2)` | `0.00%` to `100.00%` | Derived from `(market_price - sale_price) / market_price` when available, with realistic category-bounded synthetic margin assignments (e.g. 15%-45%). |
| `inventory_count` | `INT` | `0` to `500+` units | Simulates stock levels across fulfillment centers to test low-inventory penalties and out-of-stock guardrails. |
| `quality_score` | `NUMERIC(3,2)` | `0.00` to `1.00` | Normalized rating / return-rate proxy to prevent promoting high-margin but poor-quality items. |
| `business_priority`| `NUMERIC(3,2)` | `0.00` to `1.00` | Strategic campaign priority multiplier (e.g., promotional campaigns or clearance items). |
| `is_synthetic` | `BOOLEAN` | `TRUE` / `FALSE` | Explicitly tracks whether fields are synthetically augmented to maintain data auditability. |

---

## Architectural Separation
1. **Machine Learning Untouched**: The collaborative filtering (TruncatedSVD) and content-based filtering (TF-IDF) models are trained strictly on user behavior and catalog text signals.
2. **Re-Ranking Layer Isolation**: Synthetic business fields are evaluated strictly inside the **Business Guardrail Layer** during post-scoring re-ranking and never leak into the collaborative matrix factorization or TF-IDF representations.
