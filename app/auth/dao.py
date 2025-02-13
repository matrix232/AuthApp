from app.DAO.base import BaseDAO
from app.auth.models import User, Role


class RoleDAO(BaseDAO):
    model = Role


class UserDAO(BaseDAO):
    model = User
