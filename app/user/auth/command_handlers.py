from app.exceptions.application import DomainException
from app.user.auth.commands import CreateUser
from app.user.domain.entity import User
from app.utils.commandbus.abc import CommandHandler


class CreateUserHandler(CommandHandler):

    def __init__(self, user_mapper, password_hasher):
        self.user_mapper = user_mapper
        self.password_hasher = password_hasher

    async def handle(self, command: CreateUser):
        user = await self.user_mapper.find_one_by(
            email=command.email
        )
        if user is not None:
            raise DomainException(
                f"User with email '{command.email}' already exists.",
                {"email": command.email}
            )

        hashed_password = await self.password_hasher.generate(command.password)

        user = User(
            id=command.id,
            first_name=command.first_name,
            last_name=command.last_name,
            patronymic=command.patronymic,
            email=command.email,
            password=hashed_password,
            role=command.role
        )

        return user
