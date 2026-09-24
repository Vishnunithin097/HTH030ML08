"""
Seed script for cold start demo users and items in PostgreSQL.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.session import SessionLocal
from app.models.db_models import User, Item, BusinessMetadata


def seed_cold_start():
    db = SessionLocal()
    try:
        # Check / create demo user
        user = db.query(User).filter_by(user_id=999999999).first()
        if not user:
            user = User(
                user_id=999999999,
                signup_date=datetime.utcnow(),
                selected_categories=["Sports", "Running", "Fitness"],
                is_synthetic_cold_demo=True,
            )
            db.add(user)
            print("✓ Seeded Cold-Start Demo User: 999999999")

        # Check / create demo item
        item = db.query(Item).filter_by(item_id=999999998).first()
        if not item:
            item = Item(
                item_id=999999998,
                name="Demo Running Shoe",
                category_id=9999,
                category_name="Sports",
                subcategory="Running",
                brand="DemoBrand",
                description="Lightweight running shoe designed for daily training and fitness activities.",
                price=4999.00,
                rating=4.50,
                image_url="https://via.placeholder.com/400x400?text=Running+Shoe",
                tags=["running", "sports", "fitness", "shoes"],
                created_at=datetime.utcnow(),
                is_synthetic_cold_demo=True,
            )
            db.add(item)
            db.flush()

            meta = BusinessMetadata(
                item_id=999999998,
                margin_pct=35.00,
                inventory_count=100,
                quality_score=0.90,
                business_priority=0.80,
                is_synthetic=True,
            )
            db.add(meta)
            print("✓ Seeded Cold-Start Demo Item & Business Metadata: 999999998")

        db.commit()
    except Exception as e:
        db.rollback()
        print("✗ Seeding cold-start error:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_cold_start()
