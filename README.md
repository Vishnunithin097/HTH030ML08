# Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails

A high-performance, three-tier e-commerce recommendation system architecture integrating collaborative filtering, content-based recommendation, cold-start handling, and an independent business guardrail re-ranking layer with signal-backed explainability.

---

## 📌 Project Architecture Overview

The system strictly enforces separation of concerns across three decoupled layers:

```
┌─────────────────────────────────────────────────────────────┐
│                 1. Recommendation Engine                    │
│  - RetailRocket TruncatedSVD Collaborative Filtering        │
│  - BigBasket TF-IDF Content-Based Filtering                 │
│  - Hybrid Weighted Blending & Cold-Start Fallbacks          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Relevance Scores
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. Business Guardrail Layer                 │
│  - Real-time Re-ranking (Margin, Inventory, Quality)        │
│  - Configurable Constraints & Thresholds in PostgreSQL      │
│  - Hard / Soft Filtering Modes (Admin Managed)              │
└──────────────────────────────┬──────────────────────────────┘
                               │ Final Guarded Recommendations
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             3. Explainability & Presentation Layer          │
│  - Deterministic, signal-derived explanations               │
│  - React 18 + TypeScript + Vite + Tailwind CSS Dashboard   │
│  - Interactive Cold-Start Demo & Admin Configuration UI     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

* **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PostgreSQL (pgcrypto), AsyncPG / Psycopg2
* **Machine Learning**: scikit-learn, pandas, numpy, scipy, joblib
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
│   ├── RetailRocket/       # SVD model, user & item factors, label encoders
│   └── BigBasket/          # TF-IDF matrix, vectorizer, product metadata
│
├── backend/
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/            # Database schema migrations
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── config.py       # Pydantic Settings
│   │   ├── auth/           # JWT authentication & security
│   │   ├── api/            # Route controllers
│   │   ├── core/           # Data loaders & catalog abstraction
│   │   ├── recommenders/   # Collaborative, Content-Based, Hybrid, Cold-Start
│   │   ├── business/       # Guardrails, re-ranker, revenue impact
│   │   ├── explainability/ # Signal-backed explanation engine
│   │   ├── diversity/      # Intra-list diversity metrics
│   │   ├── evaluation/     # Ranking & business metrics
│   │   ├── models/         # Pydantic schemas & SQLAlchemy ORM models
│   │   └── db/             # Database session management
│   ├── data/               # Raw & processed data folders
│   └── scripts/            # Database seeding & inspection scripts
│
├── frontend/               # React + TypeScript + Vite + Tailwind application
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│
└── docs/                   # Architecture, API, Dataset & Demo documentation
```

---

## 🚀 Quick Start (Phase 1)

### 1. Database & Migrations
```bash
# Copy environment configuration
cp .env.example .env

# Run database migrations
cd backend
alembic upgrade head
```

### 2. Run Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
Health Check: `http://localhost:8000/health` -> `{"status": "ok"}`

### 3. Run Frontend Server
```bash
cd frontend
npm install
npm run dev
```

---

## 🛡️ Synthetic Business Data Notice
For transparency regarding synthetic business metadata (inventory, margin percentages, and quality scores) generated for hackathon benchmarking, see [README_synthetic_fields.md](file:///e:/Cold-Start-Aware-Recommendation-Engine-with-Business-Guardrails-/README_synthetic_fields.md).
