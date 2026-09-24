"""
Phase 1 Foundation Verification Test Script.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.data_loader import model_loader
from app.db.session import Base
from fastapi.testclient import TestClient


def run_verification():
    print("1. Testing FastAPI /health endpoint...")
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert res.json() == {"status": "ok"}, f"Expected {{'status': 'ok'}}, got {res.json()}"
    print("   [+] /health returned 200 OK: {'status': 'ok'}")

    print("\n2. Testing Table Metadata Declarations in SQLAlchemy...")
    expected_tables = {
        "users",
        "items",
        "interactions",
        "business_metadata",
        "guardrail_config",
        "recommendation_logs",
        "admins",
    }
    declared_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(declared_tables), f"Missing tables: {expected_tables - declared_tables}"
    print(f"   [+] All {len(declared_tables)} tables declared in ORM:")
    for t in sorted(declared_tables):
        print(f"       - {t} (columns: {len(Base.metadata.tables[t].columns)})")

    print("\n3. Testing Model Artifact Loader (RetailRocket & BigBasket)...")
    rr = model_loader.load_retailrocket_artifacts()
    assert rr["svd_model"] is not None
    assert rr["user_factors"].shape == (22141, 100)
    assert rr["item_factors"].shape == (56987, 100)
    assert len(rr["user_encoder"].classes_) == 873314
    assert len(rr["item_encoder"].classes_) == 194775
    print("   [+] RetailRocket artifacts verified.")

    bb = model_loader.load_bigbasket_artifacts()
    assert len(bb["tfidf_vectorizer"].vocabulary_) == 31138
    assert bb["tfidf_matrix"].shape == (23541, 31138)
    assert bb["product_metadata"].shape == (23541, 9)
    print("   [+] BigBasket artifacts verified.")

    print("\n4. Checking Mounted API Routes...")
    route_paths = [getattr(r, "path", str(r)) for r in app.routes]
    print(f"   [+] {len(route_paths)} routes mounted:")
    for path in sorted(set(route_paths)):
        print(f"       - {path}")

    print("\n==============================================")
    print("PHASE 1 FOUNDATION ACCEPTANCE TESTS PASSED!")
    print("==============================================")


if __name__ == "__main__":
    run_verification()
