"""
Generate deterministic product SVG visuals for every BigBasket product.

Creates: image_dataset/product_visuals/{product_id}.svg

Design:
- Pure SVG paths only (no emoji, no external fonts, no raster images)
- Category-aware color palette + abstract product shape
- Brand name + truncated product name embedded as SVG text
- Deterministic: same product_id always yields the same SVG

Run from repo root:
    python backend/scripts/generate_product_visuals.py
"""

from __future__ import annotations

import os
import re
import sys
import textwrap
from pathlib import Path

import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PARQUET_PATH = REPO_ROOT / "model" / "BigBasket" / "product_metadata.parquet"
OUTPUT_DIR = REPO_ROOT / "image_dataset" / "product_visuals"

# ── Category palette + shape key ─────────────────────────────────────────────
#
# Each entry:
#   bg_top / bg_bot   — gradient stops
#   accent            — text / stroke accent color
#   shape             — which abstract product silhouette to draw
#   label             — short human label shown in the pill
#
CATEGORY_THEMES: dict[str, dict] = {
    "beauty":    {"bg_top": "#fff1f2", "bg_bot": "#ffe4e6", "accent": "#be123c", "shape": "bottle_tall",  "label": "Beauty & Hygiene"},
    "gourmet":   {"bg_top": "#faf5ff", "bg_bot": "#f3e8ff", "accent": "#6b21a8", "shape": "jar_wide",     "label": "Gourmet & World Food"},
    "kitchen":   {"bg_top": "#f8fafc", "bg_bot": "#f1f5f9", "accent": "#334155", "shape": "box_tall",     "label": "Kitchen & Home"},
    "cleaning":  {"bg_top": "#f0fdfa", "bg_bot": "#ccfbf1", "accent": "#0f766e", "shape": "bottle_spray", "label": "Cleaning & Household"},
    "snack":     {"bg_top": "#fff7ed", "bg_bot": "#ffedd5", "accent": "#c2410c", "shape": "packet",       "label": "Snacks & Branded Foods"},
    "grain":     {"bg_top": "#fefce8", "bg_bot": "#fef9c3", "accent": "#a16207", "shape": "sack",         "label": "Foodgrains & Staples"},
    "bakery":    {"bg_top": "#fffbeb", "bg_bot": "#fef3c7", "accent": "#b45309", "shape": "box_wide",     "label": "Bakery & Dairy"},
    "beverage":  {"bg_top": "#ecfdf5", "bg_bot": "#d1fae5", "accent": "#047857", "shape": "bottle_round", "label": "Beverages"},
    "baby":      {"bg_top": "#fdf2f8", "bg_bot": "#fce7f3", "accent": "#be185d", "shape": "bottle_tall",  "label": "Baby Care"},
    "fruit":     {"bg_top": "#f0fdf4", "bg_bot": "#dcfce7", "accent": "#15803d", "shape": "produce",      "label": "Fruits & Vegetables"},
    "general":   {"bg_top": "#f8fafc", "bg_bot": "#e2e8f0", "accent": "#475569", "shape": "box_tall",     "label": "Catalog Product"},
}

def _theme(category: str, sub_category: str) -> dict:
    c = (category or "").lower()
    s = (sub_category or "").lower()
    combined = f"{c} {s}"
    if "beauty" in c or "hygiene" in c or "skin" in s or "hair" in s or "bath" in s or "groom" in s or "fragrance" in s:
        return CATEGORY_THEMES["beauty"]
    if "gourmet" in c or "world food" in c or "sauce" in s or "chocolate" in s or "spread" in s or "pickle" in s or "chutney" in s:
        return CATEGORY_THEMES["gourmet"]
    if "kitchen" in c or "garden" in c or "cookware" in s or "storage" in s or "pooja" in s:
        return CATEGORY_THEMES["kitchen"]
    if "clean" in c or "household" in c or "detergent" in s or "scrub" in s or "floor" in s:
        return CATEGORY_THEMES["cleaning"]
    if "snack" in c or "branded food" in c or "biscuit" in s or "namkeen" in s or "candy" in s or "chips" in s or "mithai" in s or "frozen" in s or "ready to cook" in s or "ready to eat" in s:
        return CATEGORY_THEMES["snack"]
    if "foodgrain" in c or "oil" in s or "masala" in s or "spice" in s or "rice" in s or "atta" in s or "dal" in s or "ghee" in s:
        return CATEGORY_THEMES["grain"]
    if "bakery" in c or "cakes" in c or "dairy" in c or "bread" in s or "milk" in s or "butter" in s or "cheese" in s:
        return CATEGORY_THEMES["bakery"]
    if "beverage" in c or "tea" in s or "coffee" in s or "juice" in s or "drink" in s or "water" in s:
        return CATEGORY_THEMES["beverage"]
    if "baby" in c or "infant" in s or "diaper" in s:
        return CATEGORY_THEMES["baby"]
    if "fruit" in c or "vegetable" in c or "veg" in c:
        return CATEGORY_THEMES["fruit"]
    return CATEGORY_THEMES["general"]


# ── SVG Shape Library (pure SVG paths, no emoji) ─────────────────────────────

def _shape_bottle_tall(color: str, accent: str) -> str:
    """Tall cosmetic / baby bottle."""
    hi = _lighten(color)
    return f"""
  <rect x="172" y="105" width="56" height="168" rx="20" fill="{color}" opacity="0.88"/>
  <rect x="184" y="68" width="32" height="40" rx="7" fill="{hi}"/>
  <rect x="190" y="56" width="20" height="14" rx="5" fill="{accent}"/>
  <ellipse cx="200" cy="188" rx="18" ry="36" fill="#ffffff" opacity="0.18"/>
  <rect x="178" y="148" width="44" height="3" rx="1.5" fill="#ffffff" opacity="0.45"/>
  <rect x="182" y="168" width="36" height="3" rx="1.5" fill="#ffffff" opacity="0.30"/>
"""

def _shape_jar_wide(color: str, accent: str) -> str:
    """Wide-mouth jar / gourmet jar."""
    hi = _lighten(color)
    return f"""
  <rect x="152" y="148" width="96" height="110" rx="14" fill="{color}" opacity="0.88"/>
  <rect x="158" y="126" width="84" height="26" rx="6" fill="{hi}"/>
  <ellipse cx="200" cy="148" rx="42" ry="10" fill="{accent}" opacity="0.55"/>
  <ellipse cx="200" cy="200" rx="30" ry="40" fill="#ffffff" opacity="0.16"/>
  <rect x="162" y="178" width="76" height="3" rx="1.5" fill="#ffffff" opacity="0.40"/>
"""

def _shape_box_tall(color: str, accent: str) -> str:
    """Upright rectangular product box."""
    hi = _lighten(color)
    return f"""
  <rect x="158" y="112" width="84" height="148" rx="10" fill="{color}" opacity="0.88"/>
  <rect x="158" y="112" width="84" height="28" rx="10" fill="{hi}"/>
  <rect x="158" y="130" width="84" height="10" fill="{hi}"/>
  <rect x="168" y="160" width="64" height="4" rx="2" fill="#ffffff" opacity="0.40"/>
  <rect x="172" y="176" width="56" height="4" rx="2" fill="#ffffff" opacity="0.28"/>
  <rect x="176" y="192" width="48" height="4" rx="2" fill="#ffffff" opacity="0.18"/>
"""

def _shape_bottle_spray(color: str, accent: str) -> str:
    """Spray/cleaning bottle."""
    hi = _lighten(color)
    return f"""
  <rect x="170" y="148" width="60" height="128" rx="14" fill="{color}" opacity="0.88"/>
  <path d="M182 148 L182 96 L162 96 L170 72 L214 72 L202 96 L202 148 Z" fill="{hi}"/>
  <rect x="170" y="168" width="60" height="4" rx="2" fill="#ffffff" opacity="0.40"/>
  <ellipse cx="200" cy="210" rx="18" ry="30" fill="#ffffff" opacity="0.18"/>
"""

def _shape_packet(color: str, accent: str) -> str:
    """Snack/food packet (tapered bag)."""
    hi = _lighten(color)
    return f"""
  <path d="M154 100 L246 100 L230 280 L170 280 Z" fill="{color}" opacity="0.88"/>
  <path d="M154 100 Q200 116 246 100 L244 116 Q200 132 156 116 Z" fill="{hi}"/>
  <rect x="168" y="158" width="64" height="3" rx="1.5" fill="#ffffff" opacity="0.45"/>
  <rect x="174" y="176" width="52" height="3" rx="1.5" fill="#ffffff" opacity="0.32"/>
  <circle cx="200" cy="198" r="20" fill="#ffffff" opacity="0.18"/>
"""

def _shape_sack(color: str, accent: str) -> str:
    """Grain/flour sack."""
    hi = _lighten(color)
    return f"""
  <path d="M158 150 Q158 108 200 108 Q242 108 242 150 L238 270 L162 270 Z" fill="{color}" opacity="0.88"/>
  <path d="M162 150 Q162 118 200 118 Q238 118 238 150" fill="none" stroke="{hi}" stroke-width="3"/>
  <rect x="178" y="55" width="44" height="56" rx="6" fill="{hi}"/>
  <rect x="188" y="44" width="24" height="14" rx="5" fill="{accent}"/>
  <rect x="172" y="188" width="56" height="3" rx="1.5" fill="#ffffff" opacity="0.40"/>
  <rect x="178" y="206" width="44" height="3" rx="1.5" fill="#ffffff" opacity="0.28"/>
"""

def _shape_box_wide(color: str, accent: str) -> str:
    """Wide horizontal box (bakery/dairy carton)."""
    hi = _lighten(color)
    return f"""
  <rect x="130" y="148" width="140" height="110" rx="12" fill="{color}" opacity="0.88"/>
  <rect x="130" y="148" width="140" height="30" rx="12" fill="{hi}"/>
  <rect x="130" y="168" width="140" height="10" fill="{hi}"/>
  <rect x="148" y="192" width="104" height="4" rx="2" fill="#ffffff" opacity="0.40"/>
  <rect x="155" y="210" width="90" height="4" rx="2" fill="#ffffff" opacity="0.28"/>
  <rect x="162" y="228" width="76" height="4" rx="2" fill="#ffffff" opacity="0.18"/>
"""

def _shape_bottle_round(color: str, accent: str) -> str:
    """Round beverage bottle."""
    hi = _lighten(color)
    return f"""
  <path d="M174 120 L226 120 L218 272 L182 272 Z" fill="{color}" opacity="0.88"/>
  <rect x="186" y="72" width="28" height="52" rx="8" fill="{hi}"/>
  <rect x="190" y="60" width="20" height="16" rx="5" fill="{accent}"/>
  <ellipse cx="200" cy="196" rx="16" ry="36" fill="#ffffff" opacity="0.20"/>
  <rect x="180" y="162" width="40" height="3" rx="1.5" fill="#ffffff" opacity="0.45"/>
"""

def _shape_produce(color: str, accent: str) -> str:
    """Round fruit/vegetable."""
    hi = _lighten(color)
    return f"""
  <circle cx="200" cy="200" r="74" fill="{color}" opacity="0.90"/>
  <ellipse cx="200" cy="190" rx="44" ry="55" fill="{hi}" opacity="0.30"/>
  <path d="M200 130 Q220 90 238 98" stroke="{accent}" stroke-width="7" stroke-linecap="round" fill="none"/>
  <ellipse cx="234" cy="102" rx="14" ry="7" fill="{hi}" transform="rotate(-20 234 102)"/>
"""

SHAPE_FNS = {
    "bottle_tall":   _shape_bottle_tall,
    "jar_wide":      _shape_jar_wide,
    "box_tall":      _shape_box_tall,
    "bottle_spray":  _shape_bottle_spray,
    "packet":        _shape_packet,
    "sack":          _shape_sack,
    "box_wide":      _shape_box_wide,
    "bottle_round":  _shape_bottle_round,
    "produce":       _shape_produce,
}

def _lighten(hex_color: str) -> str:
    """Return a lightened variant of a hex color for highlights."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, r + 60)
    g = min(255, g + 60)
    b = min(255, b + 60)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Text helpers ──────────────────────────────────────────────────────────────

def _escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))

def _truncate(s: str, max_chars: int) -> str:
    s = s.strip()
    if len(s) <= max_chars:
        return s
    return s[:max_chars - 1].rstrip() + "…"


# ── SVG Builder ───────────────────────────────────────────────────────────────

def build_svg(
    product_id: int | str,
    product_name: str,
    brand: str,
    category: str,
    sub_category: str,
) -> str:
    theme = _theme(category, sub_category)
    bg_top  = theme["bg_top"]
    bg_bot  = theme["bg_bot"]
    accent  = theme["accent"]
    shape_key = theme["shape"]
    cat_label = theme["label"]

    # Derive shape fill color from accent (darker shade for product body)
    fill_color = accent

    uid = f"pv{str(product_id).replace('-', '')}"
    shape_svg = SHAPE_FNS[shape_key](fill_color, accent)

    # Text lines
    brand_text = _escape_xml(_truncate(brand or "", 28))
    name_text  = _escape_xml(_truncate(product_name or "", 36))
    # Wrap long names to 2 lines
    name_lines = textwrap.wrap(product_name or "", width=20)
    name_line1 = _escape_xml(_truncate(name_lines[0] if name_lines else "", 20))
    name_line2 = _escape_xml(_truncate(name_lines[1] if len(name_lines) > 1 else "", 20))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="bg{uid}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{bg_top}"/>
      <stop offset="100%" stop-color="{bg_bot}"/>
    </linearGradient>
    <radialGradient id="sh{uid}" cx="50%" cy="92%" r="50%">
      <stop offset="0%" stop-color="rgba(15,23,42,0.16)"/>
      <stop offset="100%" stop-color="rgba(15,23,42,0)"/>
    </radialGradient>
    <filter id="dr{uid}" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="5" stdDeviation="9" flood-color="rgba(15,23,42,0.13)"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="400" height="400" fill="url(#bg{uid})" rx="16"/>
  <rect x="1" y="1" width="398" height="398" rx="15" fill="none"
        stroke="rgba(226,232,240,0.65)" stroke-width="1.5"/>

  <!-- Floor shadow -->
  <ellipse cx="200" cy="305" rx="112" ry="18" fill="url(#sh{uid})"/>

  <!-- Product shape -->
  <g filter="url(#dr{uid})">{shape_svg}  </g>

  <!-- Brand label (top-left pill) -->
  <rect x="20" y="20" width="160" height="24" rx="12"
        fill="#ffffff" fill-opacity="0.85" stroke="rgba(226,232,240,0.7)" stroke-width="1"/>
  <text x="100" y="36"
        font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"
        font-size="11" font-weight="700" fill="{accent}" text-anchor="middle"
        dominant-baseline="central">{brand_text}</text>

  <!-- Product name (bottom area) -->
  <rect x="24" y="316" width="352" height="58" rx="12"
        fill="#ffffff" fill-opacity="0.90" stroke="rgba(226,232,240,0.7)" stroke-width="1"/>
  <text x="200" y="334"
        font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"
        font-size="12" font-weight="600" fill="#1e293b" text-anchor="middle">{name_line1}</text>
  <text x="200" y="350"
        font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"
        font-size="12" font-weight="600" fill="#1e293b" text-anchor="middle">{name_line2}</text>
  <text x="200" y="366"
        font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"
        font-size="10" font-weight="500" fill="{accent}" text-anchor="middle">{_escape_xml(cat_label)}</text>
</svg>"""
    return svg


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  HTH030ML08 — Product Visual Generator")
    print("=" * 60)

    if not PARQUET_PATH.exists():
        print(f"ERROR: Parquet not found at {PARQUET_PATH}")
        sys.exit(1)

    df = pd.read_parquet(PARQUET_PATH)
    print(f"Loaded {len(df):,} products from {PARQUET_PATH.name}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total      = len(df)
    generated  = 0
    skipped    = 0
    failed     = 0

    for _, row in df.iterrows():
        pid = int(row["product_id"]) if "product_id" in row and pd.notna(row.get("product_id")) else int(row.get("original_index", 0))
        product_name = str(row.get("product", "") or "")
        brand        = str(row.get("brand", "")   or "")
        category     = str(row.get("category", "") or "")
        sub_category = str(row.get("sub_category", "") or "")

        out_path = OUTPUT_DIR / f"{pid}.svg"
        if out_path.exists():
            skipped += 1
            continue

        try:
            svg = build_svg(pid, product_name, brand, category, sub_category)
            out_path.write_text(svg, encoding="utf-8")
            generated += 1
        except Exception as e:
            print(f"  WARN: Failed for product_id={pid} ({product_name[:30]}): {e}")
            failed += 1

    coverage = ((generated + skipped) / total * 100) if total else 0

    print()
    print("=" * 60)
    print(f"  Total products  : {total:,}")
    print(f"  Newly generated : {generated:,}")
    print(f"  Already existed : {skipped:,}")
    print(f"  Failed          : {failed}")
    print(f"  Coverage        : {coverage:.1f}%")
    print("=" * 60)
    print(f"  Output dir: {OUTPUT_DIR}")
    print()
    if failed == 0:
        print("  SUCCESS — 100% visual coverage achieved.")
    else:
        print(f"  WARNING — {failed} products could not be generated.")


if __name__ == "__main__":
    main()
