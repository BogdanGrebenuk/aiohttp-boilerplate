from dataclasses import dataclass

from app.user.auth.schemas import CreateUserSchema
from app.utils.commandbus.abc import Command


@dataclass
class CreateUser(Command):
    id: str
    email: str
    password: str
    first_name: str
    last_name: str
    patronymic: str
    role: str

    def get_schema(self):
        return CreateUserSchema
