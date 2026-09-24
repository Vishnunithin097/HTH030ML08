# System Architecture Specification

## 1. High-Level Architecture Overview

```
+-------------------------------------------------------------------------------+
|                                React Frontend                                 |
|   - Dashboard (Recommendation Feed, Pure vs Business Mode Comparison)         |
|   - Cold Start Demo (Interactive Persona Selection & Real-Time Ingestion)     |
|   - Admin Control Center (Guardrail Config Sliders & Policy Rules)            |
|   - Analytics & Diagnostics (NDCG, Diversity, Coverage, Revenue Lift)        |
+---------------------------------------+---------------------------------------+
                                        | HTTP / REST (Axios)
                                        v
+-------------------------------------------------------------------------------+
|                                FastAPI Backend                                |
|  Routes: /auth, /recommendations, /demo, /config/guardrails, /metrics, /items  |
+-------------------+---------------------------------------+-------------------+
                    |                                       |
                    v                                       v
+-------------------------------------+   +-------------------------------------+
|        Recommendation Core          |   |       Business Guardrails Layer     |
| - Collaborative Filter (SVD)        |   | - Constraint Filters (Min Inv/Marg) |
| - Content-Based (TF-IDF Cosine)     |   | - Dynamic Re-Ranker                 |
| - Cold-Start Strategy Engine        |   | - Revenue / Margin Multiplier       |
| - Blending & Normalization          |   | - Business Policy Store             |
+-------------------+-----------------+   +-----------------+-------------------+
                    |                                       |
                    +-------------------+-------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                         Explainability Engine                                 |
|  - Feature Contribution Analysis & Category/Brand Preference Tracing          |
|  - Counterfactual Simulation Engine ("Why Not X?")                            |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                            Data & Persistence                                 |
|  - PostgreSQL 16 (Users, Items, Interactions, Business Meta, Config, Logs)    |
|  - Pre-trained Artifacts (RetailRocket SVD, BigBasket TF-IDF Vectors & Matrix)|
+-------------------------------------------------------------------------------+
```

---

## 2. Core Design Principles

### Principle 1: Structural Independence of ML & Business Rules
* The machine learning models output pure preference affinity / relevance scores $\in [0, 1]$.
* The Business Guardrail Layer takes pure relevance scores as input and applies multi-objective scalarization:
  $$\text{FinalScore} = w_{\text{rel}} \cdot \text{Relevance} + w_{\text{biz}} \cdot \text{BusinessScore} - \text{Penalties}$$
* The ML models are immutable at runtime; administrators calibrate the business layer weights without invalidating latent embeddings.

### Principle 2: Dedicated Cold-Start Handling
* Users with fewer interactions than `cold_start_threshold` are routed to the content/popularity cold-start resolver.
* New items lacking interaction history are matched via semantic similarity over TF-IDF item representations and boosted via category-specific business rules.

### Principle 3: No False Explanations
* Explanations are derived directly from user interaction history, category affinity vectors, and top TF-IDF keyword overlap.
