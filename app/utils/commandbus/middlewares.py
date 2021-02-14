import inspect
from dataclasses import asdict

from dependency_injector import providers

from app.utils.commandbus.abc import Command, CommandHandler
from app.utils.commandbus.exceptions import HandlerNotFoundException
from app.utils.commandbus.abc import Middleware


class Resolver(Middleware):

    def __init__(self, application_container):
        self._application_container = application_container
        self._init_handlers_map()

    def _init_handlers_map(self):
        self._handlers_map = {}
        for name, handler in self._get_handlers(self._application_container):
            self._handlers_map[name] = handler

    def _get_handlers(self, container):
        for _, provider in container.providers.items():
            if isinstance(provider, providers.Container):
                yield from self._get_handlers(provider())
            else:
                if (
                        not hasattr(provider, 'cls')
                        or not inspect.isclass(provider.cls)
                        or not hasattr(provider.cls, '__name__')
                        ):
                    continue
                name = provider.cls.__name__
                if issubclass(provider.cls, CommandHandler):
                    yield name, provider

    async def __call__(self, command: Command, next_: Middleware):
        command_cls = type(command).__name__
        handler_name = f"{command_cls}Handler"
        handler = self._handlers_map.get(handler_name)
        if handler is None:
            raise HandlerNotFoundException(f'there is no handler for {command_cls}!')
        return await handler().handle(command)


class Validator(Middleware):

    async def __call__(self, command: Command, next_: Middleware):
        schema = command.get_schema()
        if schema is not None:
            schema().load(asdict(command))
        return await next_(command)
