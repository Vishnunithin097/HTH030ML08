"""
Deterministic Business Metadata Generator.
Synthesizes realistic business metadata (margin, inventory, quality, priority)
for catalog items to evaluate multi-objective re-ranking and guardrail enforcement.
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.feature_extraction import feature_store
from app.db.session import SessionLocal
from app.models.db_models import Item, BusinessMetadata


def generate_business_metadata(seed: int = 42) -> pd.DataFrame:
    """
    Generates deterministic synthetic business metadata for all BigBasket products.
    """
    np.random.seed(seed)
    df = feature_store.product_metadata
    if df is None:
        raise ValueError("Product metadata not loaded in FeatureStore.")

    n = len(df)
    print(f"Generating synthetic business metadata for {n} products (Seed={seed})...")

    # 1. Margin Percentage (15% to 45%, with some low margin loss-leaders and high margin specials)
    base_margin = np.random.beta(a=3, b=5, size=n) * 40.0 + 10.0  # ~10% to 50%
    # If margin_reference in parquet is non-zero, blend it
    margin_ref = df.get("margin_reference", pd.Series(np.zeros(n))).values * 100.0
    has_ref = margin_ref > 0
    base_margin[has_ref] = 0.5 * base_margin[has_ref] + 0.5 * margin_ref[has_ref]
    margin_pct = np.clip(np.round(base_margin, 2), 5.00, 60.00)

    # 2. Inventory Count (0 to 250 units)
    # 8% low inventory / near stock-out (0-9 units) to test guardrails
    # 70% normal stock (10-100 units)
    # 22% high stock (101-250 units)
    inv_dist = np.random.rand(n)
    inventory_count = np.where(
        inv_dist < 0.08,
        np.random.randint(0, 10, size=n),
        np.where(
            inv_dist < 0.78,
            np.random.randint(10, 100, size=n),
            np.random.randint(100, 250, size=n)
        )
    )

    # 3. Quality Score (0.40 to 0.98)
    quality_score = np.clip(np.round(np.random.beta(a=6, b=2, size=n), 2), 0.40, 0.98)

    # 4. Strategic Business Priority (0.0 to 1.0, mostly 0 with 15% boosted items)
    prio_mask = np.random.rand(n) < 0.15
    business_priority = np.zeros(n, dtype=np.float64)
    business_priority[prio_mask] = np.round(np.random.uniform(0.5, 1.0, size=np.sum(prio_mask)), 2)

    meta_df = pd.DataFrame({
        "item_id": df["product_id"].astype(int),
        "margin_pct": margin_pct,
        "inventory_count": inventory_count,
        "quality_score": quality_score,
        "business_priority": business_priority,
        "is_synthetic": True,
    })

    print("Business metadata synthesis complete:")
    print(f"  - Margin Range: {meta_df['margin_pct'].min()}% - {meta_df['margin_pct'].max()}% (Mean: {meta_df['margin_pct'].mean():.1f}%)")
    print(f"  - Low-Inventory Items (<10 units): {(meta_df['inventory_count'] < 10).sum()} ({(meta_df['inventory_count'] < 10).mean()*100:.1f}%)")
    print(f"  - Priority Boosted Items: {(meta_df['business_priority'] > 0).sum()} ({(meta_df['business_priority'] > 0).mean()*100:.1f}%)")

    return meta_df


def save_to_database(meta_df: pd.DataFrame):
    """Inserts or updates business metadata records in PostgreSQL."""
    try:
        db = SessionLocal()
        print("Writing business metadata to database...")
        records = meta_df.to_dict(orient="records")
        
        # Batch insert/upsert
        count = 0
        for rec in records:
            existing = db.query(BusinessMetadata).filter_by(item_id=rec["item_id"]).first()
            if existing:
                existing.margin_pct = rec["margin_pct"]
                existing.inventory_count = rec["inventory_count"]
                existing.quality_score = rec["quality_score"]
                existing.business_priority = rec["business_priority"]
            else:
                new_meta = BusinessMetadata(**rec)
                db.add(new_meta)
            count += 1
            if count % 2000 == 0:
                db.commit()
                print(f"  Committed {count} / {len(records)} records...")
        
        db.commit()
        print(f"[+] Successfully saved {count} business metadata records to PostgreSQL.")
    except Exception as e:
        print(f"[-] Database write error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    df = generate_business_metadata()
    # If database is accessible, sync to it
    try:
        save_to_database(df)
    except Exception as err:
        print("Note: Direct DB connection optional during offline data prep:", err)
