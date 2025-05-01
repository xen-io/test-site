import hashlib
import datetime
import logging

import jwt

from fastapi import status
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select, update

from jwt.exceptions import DecodeError
from fastapi.exceptions import HTTPException

from db import AuthUser

log = logging.getLogger(__name__)


def create_engine(config):
    return create_async_engine(URL.create(
        'postgresql+asyncpg',
        config['db_user'],
        config['db_password'],
        config['db_host'],
        config['db_port'],
        config['db_name']
    ))


def hash_password(password):
    return hashlib.shake_256(password.encode()).hexdigest(20)


def gen_jwt(secret, payload):
    return jwt.encode(
        payload,
        secret,
        'HS256'
    )


async def verify_token(secret, token):
    try:
        return jwt.decode(
            token,
            secret,
            verify=True,
            algorithms='HS256'
        )
    except (DecodeError, KeyError):
        log.error('invalid token provided')
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Invalid token'
        )


async def verify_admin(engine, user_id):
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(AuthUser.is_admin).where(
                AuthUser.id == user_id
            ))
            result = result.one()
    except NoResultFound:
        log.error('invalid token provided')
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Invalid Token'
        )
    if not bool(result[0]):
        log.error(f'turns out {user_id} is not an admin')
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            'Forbidden'
        )


async def update_user(engine, id, data):
    try:
        async with engine.connect() as conn:
            result = await conn.execute(update(AuthUser).where(
                AuthUser.id == id
            ).values(**data))
            await conn.execute(update(AuthUser.updated_at).where(
                AuthUser.id == id
            ).values(datetime.datetime.now()))
            await conn.commit()
            return result
    except NoResultFound:
        log.error(f'user cannot be updated because he does not exist: {id}')
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'User does not exists'
        )
    except Exception:
        log.error(f'user cannot be updated because wrong fields provided: {data}')
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Unknown fields'
        )
