from app.services.base import BaseService
from app.users.models import Users, Role


class UserService(BaseService):
    model = Users


class RoleService(BaseService):
    model = Role


    