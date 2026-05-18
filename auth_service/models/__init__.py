"""Auth Service database models (SQLModel)."""

# Import all model modules so their tables are registered in SQLModel.metadata
# before lifespan calls metadata.create_all.
import auth_service.models.credential  # noqa: F401
import auth_service.models.permission  # noqa: F401
import auth_service.models.role  # noqa: F401
import auth_service.models.session  # noqa: F401
import auth_service.models.token  # noqa: F401
import auth_service.models.user  # noqa: F401
