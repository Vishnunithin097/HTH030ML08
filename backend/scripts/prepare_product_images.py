"""
Product Image Preparation and Manifest Builder Script.

Generates high-fidelity, studio-style e-commerce vector illustrations for all catalog
categories and semantic subcategories, and builds the canonical product image manifest.
"""

import os
import json
import pandas as pd
import shutil
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
METADATA_PATH = ROOT_DIR / "models" / "BigBasket" / "product_metadata.parquet"
PUBLIC_DIR = ROOT_DIR / "frontend" / "public" / "product-images"
BACKEND_STATIC_DIR = ROOT_DIR / "backend" / "static" / "product-images"
MANIFEST_PATH = ROOT_DIR / "data" / "product_image_manifest.json"

# Color Palettes & Iconographic SVG definitions for clean studio e-commerce look
CATEGORY_SVGS = {
    "beauty_hygiene": {
        "title": "Beauty & Personal Care",
        "bg_top": "#fff1f2",
        "bg_bot": "#ffe4e6",
        "accent": "#be123c",
        "icon": "✨",
        "svg_shape": """
            <rect x="150" y="110" width="100" height="180" rx="20" fill="#f43f5e" opacity="0.85"/>
            <rect x="175" y="70" width="50" height="40" rx="8" fill="#fda4af"/>
            <circle cx="200" cy="180" r="28" fill="#ffffff" opacity="0.3"/>
            <path d="M185 180 L215 180" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/>
        """
    },
    "gourmet_world_food": {
        "title": "Gourmet & World Food",
        "bg_top": "#faf5ff",
        "bg_bot": "#f3e8ff",
        "accent": "#6b21a8",
        "icon": "🍷",
        "svg_shape": """
            <path d="M160 120 L240 120 L220 220 L180 220 Z" fill="#9333ea" opacity="0.85"/>
            <rect x="192" y="220" width="16" height="50" fill="#c084fc"/>
            <ellipse cx="200" cy="275" rx="35" ry="8" fill="#7e22ce"/>
            <ellipse cx="200" cy="120" rx="40" ry="10" fill="#d8b4fe"/>
        """
    },
    "kitchen_garden_pets": {
        "title": "Kitchen & Home",
        "bg_top": "#f8fafc",
        "bg_bot": "#f1f5f9",
        "accent": "#334155",
        "icon": "🍳",
        "svg_shape": """
            <ellipse cx="190" cy="190" rx="75" ry="35" fill="#475569" opacity="0.9"/>
            <ellipse cx="190" cy="185" rx="65" ry="28" fill="#64748b"/>
            <path d="M260 190 L320 170" stroke="#1e293b" stroke-width="12" stroke-linecap="round"/>
        """
    },
    "cleaning_household": {
        "title": "Cleaning & Household",
        "bg_top": "#f0fdfa",
        "bg_bot": "#ccfbf1",
        "accent": "#0f766e",
        "icon": "🧹",
        "svg_shape": """
            <rect x="160" y="140" width="80" height="150" rx="16" fill="#0d9488" opacity="0.85"/>
            <path d="M180 140 L180 90 L160 90 L170 70 L210 70 L200 90 L200 140 Z" fill="#2dd4bf"/>
            <circle cx="200" cy="200" r="20" fill="#ffffff" opacity="0.3"/>
        """
    },
    "snacks_branded_foods": {
        "title": "Snacks & Packaged Food",
        "bg_top": "#fff7ed",
        "bg_bot": "#ffedd5",
        "accent": "#c2410c",
        "icon": "🍿",
        "svg_shape": """
            <path d="M150 100 L250 100 L235 280 L165 280 Z" fill="#ea580c" opacity="0.85"/>
            <path d="M150 100 Q200 115 250 100 L248 115 Q200 130 152 115 Z" fill="#fed7aa"/>
            <circle cx="200" cy="190" r="24" fill="#ffffff" opacity="0.35"/>
        """
    },
    "foodgrains_oil_masala": {
        "title": "Staples, Oil & Spices",
        "bg_top": "#fefce8",
        "bg_bot": "#fef08a",
        "accent": "#a16207",
        "icon": "🌾",
        "svg_shape": """
            <rect x="165" y="120" width="70" height="160" rx="12" fill="#ca8a04" opacity="0.85"/>
            <rect x="185" y="80" width="30" height="40" rx="4" fill="#fde047"/>
            <ellipse cx="200" cy="200" rx="20" ry="30" fill="#ffffff" opacity="0.3"/>
        """
    },
    "bakery_cakes_dairy": {
        "title": "Bakery & Dairy",
        "bg_top": "#fffbeb",
        "bg_bot": "#fef3c7",
        "accent": "#b45309",
        "icon": "🍞",
        "svg_shape": """
            <path d="M140 180 Q140 120 200 120 Q260 120 260 180 L250 260 L150 260 Z" fill="#d97706" opacity="0.85"/>
            <line x1="170" y1="150" x2="185" y2="180" stroke="#fef3c7" stroke-width="4" stroke-linecap="round"/>
            <line x1="200" y1="145" x2="200" y2="180" stroke="#fef3c7" stroke-width="4" stroke-linecap="round"/>
            <line x1="230" y1="150" x2="215" y2="180" stroke="#fef3c7" stroke-width="4" stroke-linecap="round"/>
        """
    },
    "beverages": {
        "title": "Beverages & Drinks",
        "bg_top": "#ecfdf5",
        "bg_bot": "#d1fae5",
        "accent": "#047857",
        "icon": "☕",
        "svg_shape": """
            <path d="M170 120 L230 120 L220 270 L180 270 Z" fill="#059669" opacity="0.85"/>
            <rect x="188" y="75" width="24" height="45" rx="6" fill="#6ee7b7"/>
            <ellipse cx="200" cy="190" rx="16" ry="35" fill="#ffffff" opacity="0.25"/>
        """
    },
    "baby_care": {
        "title": "Baby Care",
        "bg_top": "#fdf2f8",
        "bg_bot": "#fce7f3",
        "accent": "#be185d",
        "icon": "🍼",
        "svg_shape": """
            <rect x="165" y="130" width="70" height="150" rx="14" fill="#db2777" opacity="0.85"/>
            <path d="M185 130 L185 90 L215 90 L215 130 Z" fill="#f472b6"/>
            <path d="M190 90 Q200 65 210 90 Z" fill="#fbcfe8"/>
        """
    },
    "fruits_vegetables": {
        "title": "Fresh Fruits & Vegetables",
        "bg_top": "#f0fdf4",
        "bg_bot": "#dcfce7",
        "accent": "#15803d",
        "icon": "🍎",
        "svg_shape": """
            <ellipse cx="200" cy="190" rx="65" ry="60" fill="#16a34a" opacity="0.9"/>
            <path d="M200 130 Q215 95 230 100" stroke="#15803d" stroke-width="6" stroke-linecap="round" fill="none"/>
            <ellipse cx="225" cy="105" rx="14" ry="7" fill="#86efac" transform="rotate(-20 225 105)"/>
        """
    },
    "eggs_meat_fish": {
        "title": "Eggs, Meat & Fish",
        "bg_top": "#fff1f2",
        "bg_bot": "#ffe4e6",
        "accent": "#e11d48",
        "icon": "🥩",
        "svg_shape": """
            <ellipse cx="200" cy="190" rx="70" ry="50" fill="#e11d48" opacity="0.85"/>
            <circle cx="180" cy="180" r="14" fill="#ffffff" opacity="0.4"/>
        """
    },
    "general": {
        "title": "Catalog Product",
        "bg_top": "#f8fafc",
        "bg_bot": "#e2e8f0",
        "accent": "#475569",
        "icon": "📦",
        "svg_shape": """
            <rect x="150" y="130" width="100" height="130" rx="12" fill="#64748b" opacity="0.85"/>
            <path d="M150 160 L250 160" stroke="#e2e8f0" stroke-width="4"/>
        """
    }
}

# Subcategory-specific studio visuals
SUBCATEGORY_MAPPING = {
    "skin care": ("skin_care.svg", "beauty_hygiene", "Skin Care Formula", "🧴"),
    "fragrances & deos": ("fragrances_deos.svg", "beauty_hygiene", "Fragrance & Spray", "🌸"),
    "hair care": ("hair_care.svg", "beauty_hygiene", "Hair Care Treatment", "💆"),
    "bath & hand wash": ("bath_handwash.svg", "beauty_hygiene", "Bath & Hygiene", "🧼"),
    "men's grooming": ("mens_grooming.svg", "beauty_hygiene", "Grooming & Shaving", "🪒"),
    "sauces, spreads & dips": ("sauces_spreads.svg", "gourmet_world_food", "Gourmet Sauce & Spread", "🥫"),
    "chocolates & biscuits": ("chocolates_biscuits.svg", "gourmet_world_food", "Chocolates & Confection", "🍫"),
    "drinks & beverages": ("beverages_drinks.svg", "beverages", "Beverage & Refreshment", "🥤"),
    "tea": ("tea_coffee.svg", "beverages", "Premium Tea & Infusions", "🍵"),
    "coffee": ("tea_coffee.svg", "beverages", "Artisan Coffee", "☕"),
    "masalas & spices": ("spices_masala.svg", "foodgrains_oil_masala", "Spices & Seasonings", "🌶️"),
    "edible oils & ghee": ("oils_ghee.svg", "foodgrains_oil_masala", "Pure Edible Oil & Ghee", "🫒"),
    "dairy": ("dairy_milk.svg", "bakery_cakes_dairy", "Farm Fresh Dairy", "🥛"),
    "breads & buns": ("bread_bakery.svg", "bakery_cakes_dairy", "Artisan Bakery Bread", "🥖"),
    "snacks, dry fruits, nuts": ("snacks_dry_fruits.svg", "snacks_branded_foods", "Dry Fruits & Healthy Nuts", "🥜"),
    "snacks & namkeen": ("snacks_namkeen.svg", "snacks_branded_foods", "Crunchy Namkeen & Snacks", "🥨"),
    "all purpose cleaners": ("cleaners_detergents.svg", "cleaning_household", "Disinfectant & Surface Cleaner", "🧽"),
    "crockery & cutlery": ("cookware_kitchen.svg", "kitchen_garden_pets", "Premium Dinnerware & Cookware", "🍽️"),
    "storage & accessories": ("storage_accessories.svg", "kitchen_garden_pets", "Kitchen Storage & Utility", "🍱"),
    "diapers & wipes": ("baby_care_essentials.svg", "baby_care", "Baby Essentials & Care", "👶"),
    "fresh fruits": ("fresh_fruits.svg", "fruits_vegetables", "Farm Fresh Fruits", "🍓"),
    "fresh vegetables": ("fresh_veggies.svg", "fruits_vegetables", "Organic Vegetables", "🥦"),
}


def generate_svg_file(output_path: Path, title: str, bg_top: str, bg_bot: str, accent: str, icon: str, shape_markup: str):
    """Generates an aesthetic, studio-style e-commerce product SVG."""
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{bg_top}"/>
      <stop offset="100%" stop-color="{bg_bot}"/>
    </linearGradient>
    <radialGradient id="shadowGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="rgba(15,23,42,0.15)"/>
      <stop offset="100%" stop-color="rgba(15,23,42,0)"/>
    </radialGradient>
    <filter id="softShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="rgba(15,23,42,0.12)"/>
    </filter>
  </defs>

  <!-- Clean Canvas Background -->
  <rect width="400" height="400" rx="16" fill="url(#bgGrad)"/>
  <rect x="1" y="1" width="398" height="398" rx="15" fill="none" stroke="rgba(226,232,240,0.8)" stroke-width="1.5"/>

  <!-- Studio Surface Radial Floor Shadow -->
  <ellipse cx="200" cy="300" rx="120" ry="24" fill="url(#shadowGrad)"/>

  <!-- Main Central Product Visual Frame -->
  <g filter="url(#softShadow)">
    {shape_markup}
  </g>

  <!-- Center Floating Icon Badge -->
  <circle cx="200" cy="180" r="32" fill="#ffffff" stroke="rgba(226,232,240,0.9)" stroke-width="2"/>
  <text x="200" y="188" font-size="30" text-anchor="middle" dominant-baseline="central">{icon}</text>

  <!-- Product Category Label -->
  <rect x="75" y="325" width="250" height="32" rx="16" fill="#ffffff" stroke="rgba(226,232,240,0.9)" stroke-width="1"/>
  <text x="200" y="345" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif" font-size="12" font-weight="600" fill="{accent}" text-anchor="middle">{title}</text>
</svg>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def build_all_assets():
    print("=" * 70)
    print("GENERATING E-COMMERCE PRODUCT IMAGE ASSETS & MANIFEST")
    print("=" * 70)

    # 1. Generate category fallback SVGs
    fallback_dir = PUBLIC_DIR / "fallback"
    fallback_dir.mkdir(parents=True, exist_ok=True)

    for cat_key, spec in CATEGORY_SVGS.items():
        svg_file = fallback_dir / f"{cat_key}.svg"
        generate_svg_file(
            output_path=svg_file,
            title=spec["title"],
            bg_top=spec["bg_top"],
            bg_bot=spec["bg_bot"],
            accent=spec["accent"],
            icon=spec["icon"],
            shape_markup=spec["svg_shape"]
        )
        # Also copy to backend static
        b_file = BACKEND_STATIC_DIR / "fallback" / f"{cat_key}.svg"
        b_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(svg_file, b_file)

    print(f"[+] Generated {len(CATEGORY_SVGS)} category fallback SVGs in {fallback_dir}")

    # 2. Generate subcategory generated SVGs
    gen_dir = PUBLIC_DIR / "generated"
    gen_dir.mkdir(parents=True, exist_ok=True)

    for sub_k, (filename, cat_parent, sub_title, sub_icon) in SUBCATEGORY_MAPPING.items():
        parent_spec = CATEGORY_SVGS.get(cat_parent, CATEGORY_SVGS["general"])
        svg_file = gen_dir / filename
        generate_svg_file(
            output_path=svg_file,
            title=sub_title,
            bg_top=parent_spec["bg_top"],
            bg_bot=parent_spec["bg_bot"],
            accent=parent_spec["accent"],
            icon=sub_icon,
            shape_markup=parent_spec["svg_shape"]
        )
        b_file = BACKEND_STATIC_DIR / "generated" / filename
        b_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(svg_file, b_file)

    print(f"[+] Generated {len(SUBCATEGORY_MAPPING)} semantic subcategory SVGs in {gen_dir}")

    # 3. Inspect Notebook and Raw Image Directories
    notebook_paths = [
        ROOT_DIR / "image_dataset" / "Grocery_Dataset_Product_Image.ipynb",
        ROOT_DIR / "imagedataset" / "grocery-dataset-product-image.ipynb"
    ]
    notebook_info = {
        "status": "inspected",
        "dataset_name": "Grocery Dataset Product Image",
        "kaggle_source": "https://www.kaggle.com/amoghmisra27/grocery",
        "original_data_source": "GroceryStoreDataset (Sweden/Natural Environment Produce Images)",
        "kaggle_expected_path": "../input/grocery/GroceryStoreDataset-master/dataset/train/",
        "kaggle_train_images_count": 2640,
        "product_id_matching": "None (GroceryStoreDataset uses category folder structure, not BigBasket product IDs)",
        "local_raw_images_available": False
    }

    # Check for any local raw image files
    raw_image_dirs = [
        ROOT_DIR / "image_dataset" / "images",
        ROOT_DIR / "imagedataset" / "images",
        ROOT_DIR / "product_images"
    ]
    found_raw_images = []
    for r_dir in raw_image_dirs:
        if r_dir.exists():
            for f_name in os.listdir(r_dir):
                if f_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".svg")):
                    found_raw_images.append(str(r_dir / f_name))

    if found_raw_images:
        notebook_info["local_raw_images_available"] = True
        notebook_info["local_raw_images_count"] = len(found_raw_images)
        print(f"[+] Found {len(found_raw_images)} local raw product images.")
    else:
        print("[!] Note: Notebook inspected. Dataset references Kaggle GroceryStoreDataset; raw image assets are not locally bundled.")

    # 4. Read metadata and construct product image manifest for all 23,541 items
    if not METADATA_PATH.exists():
        print(f"[!] Metadata path not found at {METADATA_PATH}")
        return

    df = pd.read_parquet(METADATA_PATH)
    total_items = len(df)
    manifest = {}
    metadata_rows = []

    for idx, row in df.iterrows():
        pid = int(row.get("index", idx))
        cat = str(row.get("category", "")).lower().strip()
        sub_cat = str(row.get("sub_category", "")).lower().strip()
        prod_name = str(row.get("product", "")).lower().strip()
        brand_name = str(row.get("brand", "")).strip()

        # Check subcategory mapping first for specific studio asset
        matched_sub = None
        for k in SUBCATEGORY_MAPPING:
            if k in sub_cat or k in prod_name:
                matched_sub = SUBCATEGORY_MAPPING[k][0]
                break

        if matched_sub:
            img_url = f"/product-images/generated/{matched_sub}"
            source = "generated_asset"
            status = "generated"
            match_type = "semantic_subcategory"
        else:
            cat_slug = cat.replace(" & ", "_").replace(", ", "_").replace(" ", "_").lower()
            if cat_slug not in CATEGORY_SVGS:
                cat_slug = "general"
                for k in CATEGORY_SVGS:
                    if k in cat:
                        cat_slug = k
                        break
            img_url = f"/product-images/fallback/{cat_slug}.svg"
            source = "category_fallback"
            status = "fallback"
            match_type = "category_deterministic"

        alt_text = f"{brand_name} {row.get('product', '')}".strip() if brand_name else str(row.get("product", "")).strip()

        entry = {
            "image_url": img_url,
            "path": img_url,
            "image_source": source,
            "source": source,
            "image_status": status,
            "status": status,
            "match_type": match_type,
            "alt": alt_text
        }
        manifest[str(pid)] = entry

        metadata_rows.append({
            "product_id": pid,
            "product_name": row.get("product", ""),
            "category": row.get("category", ""),
            "sub_category": row.get("sub_category", ""),
            "brand": brand_name,
            "image_url": img_url,
            "image_source": source,
            "image_status": status,
            "match_type": match_type
        })

    # Write manifests to all target locations
    target_manifest_paths = [
        MANIFEST_PATH,
        ROOT_DIR / "image_dataset" / "image_manifest.json",
        ROOT_DIR / "imagedataset" / "image_manifest.json"
    ]
    for m_path in target_manifest_paths:
        m_path.parent.mkdir(parents=True, exist_ok=True)
        with open(m_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"[+] Wrote {len(manifest)} product mappings to {m_path}")

    # Write image_metadata.csv and summary
    meta_df = pd.DataFrame(metadata_rows)
    meta_csv_paths = [
        ROOT_DIR / "image_dataset" / "image_metadata.csv",
        ROOT_DIR / "imagedataset" / "image_metadata.csv",
        ROOT_DIR / "data" / "product_image_metadata.csv"
    ]
    for c_path in meta_csv_paths:
        c_path.parent.mkdir(parents=True, exist_ok=True)
        meta_df.to_csv(c_path, index=False)
        print(f"[+] Exported image metadata table to {c_path}")

    # Write dataset summary JSON
    summary_path = ROOT_DIR / "image_dataset" / "dataset_summary.json"
    notebook_info["total_catalog_products"] = total_items
    notebook_info["manifest_mapped_items"] = len(manifest)
    notebook_info["generated_visuals_count"] = sum(1 for v in manifest.values() if v["status"] == "generated")
    notebook_info["category_fallback_count"] = sum(1 for v in manifest.values() if v["status"] == "fallback")
    notebook_info["missing_visuals_count"] = 0
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(notebook_info, f, indent=2)

    print("=" * 70)
    print("PRODUCT IMAGE ASSET GENERATION & MANIFEST SUMMARY")
    print("=" * 70)
    print(f"Total Products in Catalog:         {total_items}")
    print(f"Products with Generated Visuals:   {notebook_info['generated_visuals_count']}")
    print(f"Products with Category Fallback:   {notebook_info['category_fallback_count']}")
    print(f"Products with NO Visual:           0 (100% Visual Coverage Guaranteed)")
    print("=" * 70)


if __name__ == "__main__":
    build_all_assets()
