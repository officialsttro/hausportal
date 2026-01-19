# Import Base class first
from app.db.base_class import Base  # noqa: F401

# Import all models so Alembic can discover them
from app.models.tenant import Tenant  # noqa: F401,E402
from app.models.user import User  # noqa: F401,E402
from app.models.invite import Invite  # noqa: F401,E402
from app.models.property import Property  # noqa: F401,E402
from app.models.unit import Unit  # noqa: F401,E402
from app.models.user_unit import UserUnit  # noqa: F401,E402
from app.models.ticket import Ticket  # noqa: F401,E402
from app.models.document import Document  # noqa: F401,E402
