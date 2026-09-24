"""
Product Image Coverage Audit Script.
Validates that 100% of catalog products have a valid, deterministic visual resolution
and asserts that products with no visual = 0.
"""

import os
import json
import sys
import pandas as pd
from pathlib import Path

# Set up paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.image_provider import image_provider
from app.config import settings

def audit_coverage():
    metadata_path = ROOT_DIR / "models" / "BigBasket" / "product_metadata.parquet"
    if not metadata_path.exists():
        print(f"[ERROR] Metadata not found at {metadata_path}")
        return False

    df = pd.read_parquet(metadata_path)
    total_products = len(df)

    verified_count = 0
    local_count = 0
    generated_count = 0
    fallback_count = 0
    missing_count = 0

    print("=" * 70)
    print("RUNNING PRODUCT IMAGE COVERAGE AUDIT")
    print("=" * 70)

    for idx, row in df.iterrows():
        pid = int(row.get("index", idx))
        pname = str(row.get("product", ""))
        cat = str(row.get("category", ""))
        sub_cat = str(row.get("sub_category", ""))
        brand = str(row.get("brand", ""))

        resolved = image_provider.resolve_product_image(
            product_id=pid,
            product_name=pname,
            category=cat,
            sub_category=sub_cat,
            brand=brand
        )

        status = resolved.get("image_status", "missing")
        url = resolved.get("image_url")

        if not url:
            missing_count += 1
        elif status == "verified":
            verified_count += 1
        elif status == "local":
            local_count += 1
        elif status == "generated":
            generated_count += 1
        elif status == "fallback":
            fallback_count += 1
        else:
            missing_count += 1

    print(f"Total products:                    {total_products}")
    print(f"Products with verified images:     {verified_count}")
    print(f"Products with local images:        {local_count}")
    print(f"Products with generated images:    {generated_count}")
    print(f"Products using category fallback:  {fallback_count}")
    print(f"Products with NO visual:           {missing_count}")
    print("-" * 70)

    if missing_count == 0:
        print("[SUCCESS] 100% Visual Coverage Achieved! Products with no visual = 0.")
        print("=" * 70)
        return True
    else:
        print(f"[FAILURE] {missing_count} products have missing visuals!")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = audit_coverage()
    sys.exit(0 if success else 1)
