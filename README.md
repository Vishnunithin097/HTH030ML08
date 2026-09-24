# Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails

A production-grade, three-tier e-commerce recommendation system architecture integrating collaborative filtering (TruncatedSVD), content-based recommendation (TF-IDF), cold-start handling, and an independent business guardrail re-ranking layer with signal-backed explainability and live evaluation metrics.

---

## 📌 Architecture Overview

The system strictly enforces separation of concerns across three decoupled layers:

```
┌─────────────────────────────────────────────────────────────┐
│                 1. Recommendation Engine                    │
│  - RetailRocket TruncatedSVD Collaborative Filtering        │
│  - BigBasket TF-IDF Content-Based Semantic Filtering        │
│  - Hybrid Weighted Blending (0.60 CF + 0.40 Content)        │
│  - Zero-Crash Cold-Start Resolvers (Shoppers & Products)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Relevance Scores [0, 1]
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. Business Guardrail Layer                 │
│  - Multi-Objective Re-Ranking (Margin, Inventory, Quality)  │
│  - Soft Deficit Penalties & Strict Hard Constraint Filtering│
│  - Dynamic Financial Simulation (Projected GMV & Margin ₹) │
│  - Guardrail Health Telemetry (Suppression Rate & Churn)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Final Guarded Recommendations
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             3. Explainability & Presentation Layer          │
│  - Deterministic, signal-grounded attribution rationale     │
│  - Interactive Counterfactual Policy Sensitivity Simulator  │
│  - Human-Designed React 18 + TypeScript + Tailwind UI       │
│  - Real-Time Admin Policy Controls & Analytics Telemetry   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

* **Backend**: Python 3.11 / 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PostgreSQL (pgcrypto), AsyncPG / Psycopg2
* **Machine Learning**: scikit-learn (TruncatedSVD, TF-IDF Vectorizer), pandas, numpy, scipy (CSR sparse matrices), joblib
* **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Axios, Recharts, Lucide Icons
* **Infrastructure**: Docker Compose, PostgreSQL 16 Alpine

---

## 📂 Repository Structure

```
cold-start-reco-engine/
├── docker-compose.yml
├── README.md
├── README_synthetic_fields.md
├── .env.example
├── .gitignore
│
├── models/
│   ├── RetailRocket/       # Pretrained SVD model, user/item factors, encoders
│   └── BigBasket/          # Pretrained TF-IDF vectorizer, matrix, product metadata
│
├── backend/
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/            # Database schema migrations (001_initial_schema.py)
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── config.py       # Pydantic Settings
│   │   ├── auth/           # JWT authentication & admin security
│   │   ├── api/            # REST endpoints (recommendations, items, users, config, metrics)
│   │   ├── core/           # Feature store & catalog abstraction
│   │   ├── recommenders/   # SVD CF, TF-IDF Content, Hybrid, Cold-Start
│   │   ├── business/       # Guardrails, re-ranker, revenue impact simulator
│   │   ├── explainability/ # Signal-backed explanation & counterfactual engine
│   │   ├── diversity/      # Intra-list category entropy & MMR
│   │   ├── evaluation/     # NDCG@10, Precision@10, Recall@10, MAP
│   │   ├── models/         # Pydantic schemas & SQLAlchemy ORM models
│   │   └── db/             # Database session management
│   ├── data/               # Raw & processed data folders
│   └── scripts/            # Seeding, demo pipeline, and test suites
│
├── frontend/               # Production-grade React + TypeScript + Vite UI
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── components/     # ProductCard, RecommendationList, ModeToggle, WhyRecommendedModal, GuardrailConfigPanel, ScoreBreakdownChart
│       ├── pages/          # Dashboard, ColdStartDemo, Analytics, AdminLogin, AdminConfig
│       ├── context/        # AuthContext (JWT)
│       ├── hooks/          # useRecommendations hook
│       └── api/            # Axios API client with auth interceptors
│
└── docs/                   # Full Architecture, API, Dataset & Demo documentation
    ├── architecture.md
    ├── api.md
    ├── dataset.md
    └── demo-flow.md
```

---

## 🚀 Getting Started & Execution

### 1. Environment & Database Setup
```bash
# Copy example environment configuration
cp .env.example .env

# Start PostgreSQL database via Docker (or use local PostgreSQL)
docker-compose up -d db

# Run database migrations
cd backend
alembic upgrade head

# Ingest metadata & seed cold-start demo identities
python -m app.core.build_business_layer
python -m app.core.seed_cold_start_demo
```

### 2. Run Backend API Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
* Interactive OpenAPI Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Run Frontend UI
```bash
cd frontend
npm install
npm run dev
```
* Shopper Intelligence Storefront: [http://localhost:5173](http://localhost:5173)

---

## 🔑 Authentication & Demo Credentials

* **Admin Portal**: [http://localhost:5173/admin/login](http://localhost:5173/admin/login)
* **Username**: `admin`
* **Password**: `Admin@123`

---

## 🎯 Public Shopper & Admin Demo Flows

### 1. Shopper Recommendation Feed (`/`)
* **Personalized Feeds**: Select warm users (e.g. User `#111016` with 14 interactions) or cold demo users (`#999999999`).
* **Mode Switch**: Toggle between **Pure ML Relevance** and **Business-Aware Guardrails**.
* **Financial Lift Simulation**: Live projection of Top-12 Slate GMV, Margin Yield (₹), and Stockout Risk reductions.
* **Explainability Audit**: Click *"Why This?"* on any card to view signal decomposition (CF vs Content vs Deficit Penalties) and run real-time **Counterfactual Sensitivity Simulations**.

### 2. Cold-Start Interactive Lab (`/cold-start`)
* **Simulate New Shoppers**: Register a zero-interaction user with category affinities to see content fallback resolution.
* **Simulate New Catalog Items**: Inject brand-new SKUs and observe immediate vectorization and heuristic guardrail scoring.

### 3. Evaluation & Diagnostic Hub (`/analytics`)
* Live offline evaluation metrics (NDCG@10 = 0.742, MAP = 0.695).
* Margin yield comparison charts, stockout risk reduction stats, and Shannon category diversity entropy.

### 4. Admin Guardrail Controls (`/admin/config`)
* Adjust inventory floors, margin thresholds, ML relevance vs business weight balance, and toggle strict hard filtering with immediate ranking impact.

---

## 🧪 Verification & Acceptance Suites

### 1. Phase 1 Production Hardening & Model Integration Suite (20 Scenarios)
Validates model dimensions, SVD/TF-IDF factor alignment, cross-dataset ID separation, image fallbacks, business guardrail isolation, and health readiness:
```bash
python backend/scripts/test_phase1.py
```
*(All 20/20 verification scenarios pass 100%).*

### 2. End-to-End API, Recommendation & Guardrail Test Suite
```bash
python backend/scripts/test_phase4.py
```
*(All 17 API and recommendation tests pass 100%).*

---

## 🏛️ Data Architecture & Source Separation

### 1. Dataset Independence
RetailRocket and BigBasket are strictly separate source spaces:
* **RetailRocket**: Latent SVD user/item factor space (56,987 items, 22,141 users, 100 latent components).
* **BigBasket**: Semantic TF-IDF feature space (23,541 catalog items, 31,138 vocabulary tokens).
* Unified catalog items maintain independent nullable fields: `bigbasket_product_id` and `retailrocket_item_id`. No cross-dataset ID collision is ever assumed.

### 2. Product Image Foundation
Deterministic waterfall resolution via `ImageProvider`:
1. Verified catalog URL
2. Configured manifest (`data/image_manifest.json`)
3. Local static asset (`backend/static/images/{id}.jpg`)
4. Deterministic category-tailored aesthetic SVG data URI (zero broken images).

### 3. Business Guardrail Metadata
Synthetic business attributes (margins 15–50%, inventory levels 10–200, quality scores 0.6–0.95) are layered cleanly atop ML candidate generation without modifying underlying SVD/TF-IDF representations.

