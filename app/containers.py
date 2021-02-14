from dependency_injector import containers, providers
from dependency_injector.ext import aiohttp as ext_aiohttp

from app.db import models
from app.db.mappers.user import UserMapper
from app.middlewares import error_handler, create_jwt_middleware
from app.user.containers import UserPackageContainer
from app.user.domain.entity import User
from app.utils.commandbus import Bus
from app.utils.engine import init_engine
from app.utils.executor import (
    Executor,
    init_process_pool,
    init_thread_pool
)


class Gateways(containers.DeclarativeContainer):

    config = providers.Configuration()

    engine = providers.Resource(
        init_engine,
        database_config=config.database
    )

    process_pool = providers.Resource(init_process_pool)

    thread_pool = providers.Resource(init_thread_pool)


class ApplicationUtilsContainer(containers.DeclarativeContainer):

    gateways = providers.DependenciesContainer()

    bus = providers.Singleton(Bus)

    process_executor = providers.Singleton(
        Executor,
        pool=gateways.process_pool
    )

    thread_executor = providers.Singleton(
        Executor,
        pool=gateways.thread_pool
    )
    # TODO: logger, config?


class MappersContainer(containers.DeclarativeContainer):

    gateways = providers.DependenciesContainer()

    user_mapper = providers.Singleton(
        UserMapper,
        engine=gateways.engine,
        model=models.User,
        entity_cls=User
    )


class MiddlewareContainer(containers.DeclarativeContainer):

    mappers = providers.DependenciesContainer()

    config = providers.Configuration()

    jwt_middleware = providers.Singleton(
        create_jwt_middleware,
        token_config=config.token
    )

    error_handler = ext_aiohttp.Middleware(
        error_handler
    )


class ApplicationContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    gateways = providers.Container(
        Gateways,
        config=config
    )

    application_utils = providers.Container(
        ApplicationUtilsContainer,
        gateways=gateways
    )

    mappers = providers.Container(
        MappersContainer,
        gateways=gateways
    )

    middlewares = providers.Container(
        MiddlewareContainer,
        mappers=mappers,
        config=config
    )

    user = providers.Container(
        UserPackageContainer,
        application_utils=application_utils,
        mappers=mappers,
        config=config
    )
