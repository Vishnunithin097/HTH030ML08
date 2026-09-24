import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import sync_engine, SessionLocal
from app.models.db_models import Base, Admin, GuardrailConfig, User, Item, BusinessMetadata
from app.auth.security import get_password_hash

def init_database():
    print("[*] Creating all database tables in PostgreSQL 'coldstart_db'...")
    Base.metadata.create_all(bind=sync_engine)
    print("[+] All tables created successfully.")

    db = SessionLocal()
    try:
        # Seed default admin if not exists
        admin = db.query(Admin).filter_by(username="admin").first()
        if not admin:
            admin = Admin(
                username="admin",
                hashed_password=get_password_hash("Admin@123"),
            )
            db.add(admin)
            print("[+] Seeded default admin: admin / Admin@123")

        # Seed default guardrails config if not exists
        config = db.query(GuardrailConfig).first()
        if not config:
            config = GuardrailConfig(
                min_inventory=10,
                min_margin=20.0,
                relevance_weight=0.70,
                business_weight=0.30,
                margin_weight=0.50,
                inventory_weight=0.30,
                quality_weight=0.20,
                cold_start_threshold=5,
                hard_filter_enabled=False,
            )
            db.add(config)
            print("[+] Seeded default guardrail configuration.")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[-] Error during seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
