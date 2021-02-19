from aiohttp import web
from aiohttp_jwt import JWTMiddleware
from marshmallow import ValidationError

from app.exceptions.application import AppException


async def request_logger(request, handler, logger):
    logger.info(f"{request.method} {request.rel_url}")
    return await handler(request)


@web.middleware
async def error_handler(request, handler):
    try:
        response = await handler(request)
        return response
    except ValidationError as e:
        return web.json_response({
            'error': 'Validation error',
            'payload': e.messages
        }, status=400)
    except AppException as e:
        return web.json_response({
            'error': e.message,
            'payload': e.payload
        })
    except Exception as e:
        return web.json_response({
            'error': str(e),
            'payload': {}
        }, status=500)


def create_jwt_middleware(token_config):
    return JWTMiddleware(
        secret_or_pub_key=token_config['secret'],
        algorithms=token_config['algorithm'],
        request_property="user",
        whitelist=[
            r"/login",
            r"/register"
        ]
    )
