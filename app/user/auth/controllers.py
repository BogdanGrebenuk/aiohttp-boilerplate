import uuid

from aiohttp import web

from app.user.auth.commands import CreateUser


async def authenticate_user(request, authenticator):
    body = await request.json()

    token = await authenticator.authenticate(
        body['email'], body['password']
    )

    return web.json_response({'token': token})


async def register_user(
        request,
        bus,
        user_mapper,
        user_transformer
        ):
    body = await request.json()

    user = await bus.execute(
        CreateUser(
            id=str(uuid.uuid4()),
            email=body['email'],
            password=body['password'],
            first_name=body['first_name'],
            last_name=body['last_name'],
            patronymic=body['patronymic'],
            role=body['role']
        )
    )

    await user_mapper.create(user)

    return web.json_response(await user_transformer.transform(user))
