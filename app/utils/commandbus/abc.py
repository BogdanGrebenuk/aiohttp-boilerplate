import abc
from dataclasses import asdict, dataclass


@dataclass
class Command(abc.ABC):

    @abc.abstractmethod
    def get_schema(self):
        ...

    def to_dict(self):
        return asdict(self)


class CommandHandler(abc.ABC):

    @abc.abstractmethod
    def handle(self, command: Command):
        ...


class Middleware(abc.ABC):

    @abc.abstractmethod
    async def __call__(self, command, next_):
        ...