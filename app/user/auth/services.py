import time

import bcrypt
import jwt

from app.exceptions.application import DomainException
from app.utils.mapper import EntityNotFound


class PasswordHasher:

    def __init__(self, process_executor):
        self.process_executor = process_executor

    async def generate(self, password):
        return await self.process_executor.run(
            self._generate,
            password
        )

    @staticmethod
    def _generate(password):
        password = password.encode(encoding='utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt).decode()
        return hashed_password


class PasswordChecker:

    def __init__(self, process_executor):
        self.process_executor = process_executor

    async def check(self, user, password):
        return await self.process_executor.run(
            self._check,
            password,
            user.password
        )

    @staticmethod
    def _check(password, hashed_password):
        return bcrypt.checkpw(
            password.encode(encoding='utf-8'),
            hashed_password.encode(encoding='utf-8')
        )


class TokenGenerator:

    def __init__(self, process_executor, config):
        self.process_executor = process_executor
        self.config = config

    async def generate(self, payload):
        return await self.process_executor.run(
            self._generate,
            payload,
            self.config['expiration_time'],
            self.config['secret'],
            self.config['algorithm']
        )

    @staticmethod
    def _generate(payload, expiration_time, secret, algorithm):
        token = jwt.encode(
            {
                **payload,
                'exp': int(time.time()) + int(expiration_time)
            },
            secret,
            algorithm=algorithm
        )
        return token.decode(encoding='utf-8')


class Authenticator:

    def __init__(
            self,
            user_mapper,
            password_checker,
            token_generator
            ):
        self.user_mapper = user_mapper
        self.password_checker = password_checker
        self.token_generator = token_generator

    async def authenticate(self, email, password) -> str:
        user = await self.user_mapper.find_one_by(email=email)
        if user is None:
            raise EntityNotFound(
                f"There is no user with email {email}.",
                {'email': email}
            )
        if not await self.password_checker.check(user, password):
            raise DomainException("Password is invalid.")

        token = await self.token_generator.generate(
            {'user_id': user.id}
        )

        return token
