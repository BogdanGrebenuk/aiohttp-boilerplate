class Bus:

    def __init__(self, middlewares=None):
        if middlewares is None:
            middlewares = []
        self._middlewares = middlewares
        self._chain = _build_chain(middlewares)

    def set_middlewares(self, middlewares):
        self._middlewares = middlewares
        self._chain = _build_chain(self._middlewares)

    async def execute(self, command):
        return await self._chain(command)


def _build_chain(middlewares, execution_chain=None):
    if execution_chain is None:
        execution_chain = lambda *args: None

    for middleware in reversed(middlewares):
        execution_chain = _create_closure(middleware, execution_chain)

    return execution_chain


def _create_closure(middleware, execution_chain):
    async def handle_command(command):
        return await middleware(command, execution_chain)
    return handle_command