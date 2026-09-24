"""
Seed script for administrator credentials in PostgreSQL.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.session import SessionLocal
from app.models.db_models import Admin
from app.auth.security import get_password_hash


def seed_admin(username: str = "admin", password: str = "Admin@123"):
    db = SessionLocal()
    try:
        admin = db.query(Admin).filter_by(username=username).first()
        if not admin:
            admin = Admin(
                username=username,
                hashed_password=get_password_hash(password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print(f"✓ Seeded Admin User: {username}")
        else:
            print(f"Admin User {username} already exists.")
    except Exception as e:
        db.rollback()
        print("✗ Seeding admin error:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
