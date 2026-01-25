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
        # find or create tenant
        tenant = db.scalar(select(Tenant).where(Tenant.name == tenant_name))
        if not tenant:
            tenant = Tenant(name=tenant_name)
            db.add(tenant)
            db.flush()  # tenant.id

        # find existing admin in this tenant
        admin = db.scalar(select(User).where(User.tenant_id == tenant.id, User.email == email))

        if admin:
            admin.password_hash = hash_password(password)
            admin.role = "ADMIN"
            admin.language = "de"
            admin.status = "active"
            db.add(admin)
            db.commit()
            print(f"Updated tenant id={tenant.id}, admin user id={admin.id}")
            return 0

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
