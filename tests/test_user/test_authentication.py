from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from app.exceptions.application import DomainException
from app.main import create_app
from app.user.domain.entity import User
from app.utils.mapper import EntityNotFound


EXISTENT_EMAIL = "test_email_existent@test.com"

NON_EXISTENT_EMAIL = "test_email_non_existent@test.com"

WRONG_PASSWORD_EMAIL = "test_email_wrong_password@test.com"

EXISTENT_USER = User(
    id="test_id",
    first_name="kabab",
    last_name="kabab",
    patronymic="kabab",
    email=EXISTENT_EMAIL,
    password="Test@123",
    role="participant"
)

WRONG_ANSWER_USER = User(
    id="test_id",
    first_name="kabab",
    last_name="kabab",
    patronymic="kabab",
    email=WRONG_PASSWORD_EMAIL,
    password="Test@123",
    role="participant"
)


class MockedUserMapper:

    async def find_one_by(self, **kwargs):
        email = kwargs.get("email")
        if email is None:
            raise ValueError("Expected 'email' argument")
        print(email)
        if email == EXISTENT_EMAIL:
            return EXISTENT_USER
        elif email == WRONG_PASSWORD_EMAIL:
            return WRONG_ANSWER_USER
        return None


class MockedPasswordChecker:

    async def check(self, user, password):
        if user.email == EXISTENT_EMAIL:
            return True
        elif user.email == WRONG_PASSWORD_EMAIL:
            return False
        return False


class AuthenticationTests(AioHTTPTestCase):

    async def get_application(self):
        return create_app()

    async def setUpAsync(self):
        self.app.container.mappers.user_mapper.override(MockedUserMapper())
        self.app.container.user.password_checker.override(MockedPasswordChecker())

    async def tearDownAsync(self):
        self.app.container.mappers.user_mapper.reset_override()
        self.app.container.user.password_checker.reset_override()

    @unittest_run_loop
    async def test_successful_case(self):
        authenticator = self.app.container.user.authenticator()

        token = await authenticator.authenticate(
            EXISTENT_EMAIL, EXISTENT_USER.password
        )

        self.assertIsInstance(token, str)

    @unittest_run_loop
    async def test_non_existent_email_case(self):
        authenticator = self.app.container.user.authenticator()

        with self.assertRaises(EntityNotFound):
            await authenticator.authenticate(
                NON_EXISTENT_EMAIL, 'test_password'
            )

    @unittest_run_loop
    async def test_wrong_password_case(self):
        authenticator = self.app.container.user.authenticator()

        with self.assertRaises(DomainException):
            await authenticator.authenticate(
                WRONG_PASSWORD_EMAIL, 'test_password'
            )