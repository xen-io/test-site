import hashlib

from fastapi import status
from sqlalchemy import select, update
import jwt

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import NoResultFound
from jwt.exceptions import DecodeError
from fastapi.exceptions import HTTPException

from db import User


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
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Invalid token'
        )


async def verify_admin(engine, user_id):
    async with engine.connect() as conn:
        result = await conn.execute(select(User.is_admin).where(
            User.id == user_id
        ))
        result = result.one()
    if not bool(result[0]):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            'Forbidden'
        )


async def update_user(engine, id, data):
    try:
        async with engine.connect() as conn:
            result = await conn.execute(update(User).where(
                User.id == id
            ).values(**data))
            await conn.commit()
            return result
    except NoResultFound:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'User does not exists'
        )
    except Exception:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Unknown fields'
        )
