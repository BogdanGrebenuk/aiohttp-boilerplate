from dependency_injector import containers, providers
from dependency_injector.ext import aiohttp as ext_aiohttp

from app.user.auth.command_handlers import CreateUserHandler
from app.user.auth.controllers import register_user, authenticate_user
from app.user.auth.services import (
    PasswordHasher,
    PasswordChecker,
    TokenGenerator,
    Authenticator
)
from app.user.controllers import get_user, get_users
from app.user.transformers import UserTransformer


class UserPackageContainer(containers.DeclarativeContainer):
    application_utils = providers.DependenciesContainer()

    mappers = providers.DependenciesContainer()

    config = providers.Configuration()

    # services

    user_transformer = providers.Singleton(UserTransformer)

    password_hasher = providers.Singleton(
        PasswordHasher,
        process_executor=application_utils.process_executor
    )

    password_checker = providers.Singleton(
        PasswordChecker,
        process_executor=application_utils.process_executor
    )

    token_generator = providers.Singleton(
        TokenGenerator,
        process_executor=application_utils.process_executor,
        config=config.token
    )

    authenticator = providers.Singleton(
        Authenticator,
        user_mapper=mappers.user_mapper,
        password_checker=password_checker,
        token_generator=token_generator
    )

    # controllers

    register_user = ext_aiohttp.View(
        register_user,
        bus=application_utils.bus,
        user_mapper=mappers.user_mapper,
        user_transformer=user_transformer
    )

    authenticate_user = ext_aiohttp.View(
        authenticate_user,
        authenticator=authenticator
    )

    get_user = ext_aiohttp.View(
        get_user,
        user_mapper=mappers.user_mapper,
        user_transformer=user_transformer
    )

    get_users = ext_aiohttp.View(
        get_users,
        user_mapper=mappers.user_mapper,
        user_transformer=user_transformer
    )

    # command_handlers

    create_user_handler = providers.Singleton(
        CreateUserHandler,
        user_mapper=mappers.user_mapper,
        password_hasher=password_hasher
    )
