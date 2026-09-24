"""
Build Training Image Index.
Recursively inspects image_dataset/ for all image files (.jpg, .jpeg, .png, .webp, .bmp)
and constructs searchable metadata keywords from paths, filenames, parent directories, and category labels.

Saves index to image_dataset/train_image_index.json.
"""

import os
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_DATASET_DIR = REPO_ROOT / "image_dataset"
OUTPUT_INDEX_PATH = IMAGE_DATASET_DIR / "train_image_index.json"

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')


def normalize_text(text: str) -> List[str]:
    """Normalize text into clean lowercase token keywords."""
    if not text:
        return []
    # Replace punctuation and underscores/hyphens with spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
    return tokens


def scan_training_images() -> List[Dict[str, Any]]:
    """Recursively discover and index all image files in image_dataset."""
    indexed_images = []

    if not IMAGE_DATASET_DIR.exists():
        logger.warning(f"Directory {IMAGE_DATASET_DIR} does not exist.")
        return indexed_images

    for root, dirs, files in os.walk(IMAGE_DATASET_DIR):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(REPO_ROOT).as_posix()

                # Extract directory hierarchy
                parts = full_path.relative_to(IMAGE_DATASET_DIR).parts
                parent_folder = parts[-2] if len(parts) > 1 else ""
                category_folder = parts[0] if len(parts) > 1 else ""
                subcategory_folder = parts[1] if len(parts) > 2 else ""

                # Extract keywords from filename and path
                filename_stem = full_path.stem
                keywords = set(normalize_text(filename_stem))
                keywords.update(normalize_text(parent_folder))
                keywords.update(normalize_text(category_folder))
                keywords.update(normalize_text(subcategory_folder))

                indexed_images.append({
                    "path": rel_path,
                    "filename": file,
                    "parent_folder": parent_folder,
                    "category": category_folder,
                    "subcategory": subcategory_folder,
                    "keywords": sorted(list(keywords)),
                })

    logger.info(f"Discovered {len(indexed_images)} training images across {IMAGE_DATASET_DIR}")
    return indexed_images


def main():
    logger.info("Building training image index...")
    images = scan_training_images()

    index_data = {
        "total_images": len(images),
        "source_directory": str(IMAGE_DATASET_DIR.relative_to(REPO_ROOT)),
        "images": images,
    }

    with open(OUTPUT_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)

    logger.info(f"Successfully saved train image index to {OUTPUT_INDEX_PATH}")


if __name__ == "__main__":
    main()
