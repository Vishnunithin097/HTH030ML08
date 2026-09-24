"""
Seed script for cold start demo users and items in PostgreSQL.
Explicitly isolates demo cold entities from natural user interactions.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.session import SessionLocal
from app.models.db_models import User, Item, BusinessMetadata, Interaction


def seed_cold_start():
    db = SessionLocal()
    try:
        # 1. Seed Cold-Start Demo User (ID: 999999999)
        demo_user_id = 999999999
        user = db.query(User).filter_by(user_id=demo_user_id).first()
        if not user:
            user = User(
                user_id=demo_user_id,
                signup_date=datetime.utcnow(),
                selected_categories=["Sports", "Running", "Fitness"],
                is_synthetic_cold_demo=True,
            )
            db.add(user)
            print(f"[+] Seeded Cold-Start Demo User: #{demo_user_id}")
        else:
            user.selected_categories = ["Sports", "Running", "Fitness"]
            user.is_synthetic_cold_demo = True
            print(f"[+] Verified Cold-Start Demo User: #{demo_user_id}")

        # Ensure cold user has STRICTLY 0 interactions
        interactions_count = db.query(Interaction).filter_by(user_id=demo_user_id).count()
        if interactions_count > 0:
            db.query(Interaction).filter_by(user_id=demo_user_id).delete()
            print(f"    Purged {interactions_count} unexpected interactions for cold demo user.")

        # 2. Seed Cold-Start Demo Item (ID: 999999998)
        demo_item_id = 999999998
        item = db.query(Item).filter_by(item_id=demo_item_id).first()
        if not item:
            item = Item(
                item_id=demo_item_id,
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
            print(f"[+] Seeded Cold-Start Demo Item: #{demo_item_id}")
        else:
            item.is_synthetic_cold_demo = True
            print(f"[+] Verified Cold-Start Demo Item: #{demo_item_id}")

        # Ensure cold item has STRICTLY 0 interactions
        item_interactions = db.query(Interaction).filter_by(item_id=demo_item_id).count()
        if item_interactions > 0:
            db.query(Interaction).filter_by(item_id=demo_item_id).delete()
            print(f"    Purged {item_interactions} unexpected interactions for cold demo item.")

        # 3. Seed Business Metadata for Cold-Start Item
        meta = db.query(BusinessMetadata).filter_by(item_id=demo_item_id).first()
        if not meta:
            meta = BusinessMetadata(
                item_id=demo_item_id,
                margin_pct=35.00,
                inventory_count=100,
                quality_score=0.90,
                business_priority=0.80,
                is_synthetic=True,
            )
            db.add(meta)
        else:
            meta.margin_pct = 35.00
            meta.inventory_count = 100
            meta.quality_score = 0.90
            meta.business_priority = 0.80
            meta.is_synthetic = True

        db.commit()
        print("[+] Cold-start demo entities successfully seeded in PostgreSQL.")
    except Exception as e:
        db.rollback()
        print("[-] Seeding cold-start error:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_cold_start()
