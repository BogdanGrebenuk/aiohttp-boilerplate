import pathlib

from aiohttp import web

from app.containers import ApplicationContainer
from app.resources import setup_routes
from app.utils.commandbus.middlewares import Resolver, Validator


def get_config_path():
    return str((pathlib.Path(__file__).parent.parent / 'config' / 'config.yaml').resolve())


def create_app():
    application_container = ApplicationContainer()
    config_path = get_config_path()
    application_container.config.from_yaml(config_path)

    application_container.application_utils.bus().set_middlewares([
        Validator(),
        Resolver(application_container)
    ])

    app = web.Application(
        middlewares=[
            application_container.middlewares.error_handler,
            application_container.middlewares.jwt_middleware(),
        ]
    )
    app.container = application_container
    setup_routes(app)

    app.on_startup.append(init_resources)
    app.on_shutdown.append(shutdown_resources)

    return app


async def init_resources(app):
    app.container.gateways.init_resources()


async def shutdown_resources(app):
    app.container.gateways.shutdown_resources()


if __name__ == '__main__':
    app = create_app()

    config = app.container.config

    host = config.app.host()
    port = config.app.port()

    web.run_app(app, host=host, port=port)
