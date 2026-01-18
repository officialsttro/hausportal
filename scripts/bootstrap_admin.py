import sys

from sqlalchemy import select

from app.db.session import SessionLocal
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: poetry run python scripts/bootstrap_admin.py <tenant_name> <admin_email> <admin_password>")
        return 2

    tenant_name, email, password = sys.argv[1], sys.argv[2], sys.argv[3]

    db = SessionLocal()
    try:
        # create tenant
        tenant = Tenant(name=tenant_name)
        db.add(tenant)
        db.flush()  # get tenant.id

        # ensure no existing admin with same email in this tenant (simple for now)
        existing = db.scalar(select(User).where(User.tenant_id == tenant.id, User.email == email))
        if existing:
            print("Admin email already exists in this tenant.")
            db.rollback()
            return 1

        admin = User(
            tenant_id=tenant.id,
            email=email,
            password_hash=hash_password(password),
            role="ADMIN",
            language="de",
            status="active",
        )
        db.add(admin)
        db.commit()

        print(f"Created tenant id={tenant.id}, admin user id={admin.id}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
