import os
import json
import uuid
import datetime
import logging

from fastapi import FastAPI, status
from sqlalchemy import select, insert, delete

from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

from db import AuthUser, Base
from data import (LoginData, RegisterData, ForgotPasswordData,
                  ChangePasswordData, DeleteUserData, EditUserData,
                  UsersData, StatusData, TokenData)
from utils import (create_engine, hash_password, gen_jwt,
                   verify_admin, verify_token, update_user)


with open(os.getenv('BACKEND_CONFIG')) as f:
    config = json.load(f)

engine = create_engine(config)
app = FastAPI()

logging.basicConfig(level=logging.INFO, filename=config['logs'])
log = logging.getLogger(__name__)


@app.on_event('shutdown')
async def shutdown():
    log.info('fastapi is shutting down')
    await engine.dispose()


@app.on_event('startup')
async def startup():
    log.info('creating sql tables')
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


@app.post('/auth/login')
async def post_login(login_data: LoginData):
    pass_hash = hash_password(login_data.password)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(AuthUser.id).where(
                AuthUser.email == login_data.email
            ).where(
                AuthUser.hashed_password == pass_hash
            ))
        result = result.one()
    except NoResultFound:
        log.error(f'invalid credentials to log in: {login_data}')
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            'Invalid credentials'
        )
    log.info(f'{result[0]} is logged in')
    return TokenData(token=gen_jwt(config['jwt_secret'], {'as': str(result[0])}))


@app.post('/auth/register')
async def post_register(register_data: RegisterData):
    pass_hash = hash_password(register_data.password)
    id = uuid.uuid4()
    try:
        async with engine.connect() as conn:
            await conn.execute(insert(AuthUser).values(
                id=id,
                first_name=register_data.first_name,
                last_name=register_data.last_name,
                middle_name=register_data.middle_name,
                email=register_data.email,
                hashed_password=pass_hash,
                access_level=1,
                is_active=True,
                is_verified=False,
                is_admin=False,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            ))
            await conn.commit()
    except IntegrityError:
        log.error(f'invalid credentials to register: {register_data}')
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Invalid credentials'
        )
    log.info(f'{id} is registered')
    return StatusData(status='OK')


@app.post('/auth/forgot_password')
async def post_forgot(forgot_password_data: ForgotPasswordData):
    try:
        # по email ищется uuid пользователя
        async with engine.connect() as conn:
            result = await conn.execute(select(AuthUser.id).where(
                AuthUser.email == forgot_password_data.email
            ))
            result = result.one()
    except NoResultFound:
        log.error(f'cannot recover a password for user that does not exist: {forgot_password_data.email}')
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'User does not exist'
        )
    token = gen_jwt(config['jwt_secret'], {'forgot': str(result[0])})
    # должен email отправлятся (попозже доделаю)
    print('forgot_token:', token, sep='\n')
    log.info(f'sent password recovery email for: {forgot_password_data.email}')
    return StatusData(status='OK')


@app.post('/auth/change_password')
async def post_change(change_password_data: ChangePasswordData):
    user_id = (await verify_token(config['jwt_secret'], change_password_data.token)).get('forgot')
    pass_hash = hash_password(change_password_data.password)

    await update_user(engine, user_id, {'hashed_password': pass_hash})

    log.info(f'{user_id} changed his password')
    return StatusData(status='OK')


@app.post('/users/delete')
async def post_delete_user(delete_user_data: DeleteUserData):
    # проверка является ли пользователь админом
    user_id = (await verify_token(config['jwt_secret'], delete_user_data.token)).get('as')
    await verify_admin(engine, user_id)

    try:
        async with engine.connect() as conn:
            await conn.execute(delete(AuthUser).where(
                AuthUser.id == delete_user_data.id
            ))
            await conn.commit()
    except NoResultFound:
        log.error(f'{user_id} cannot delete user that does not exist: {delete_user_data.id}')
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'User does not exists'
        )
    log.info(f'{user_id} deleted user {delete_user_data.id}')
    return StatusData(status='OK')


@app.post('/users/edit')
async def post_edit_user(edit_user_data: EditUserData):
    # проверка является ли пользователь админом
    user_id = (await verify_token(config['jwt_secret'], edit_user_data.token)).get('as')
    await verify_admin(engine, user_id)

    await update_user(engine, edit_user_data.id, {edit_user_data.key: edit_user_data.value})

    log.info(f'{user_id} edited user {edit_user_data.id}: key={edit_user_data.key} value={edit_user_data.value}')
    return StatusData(status='OK')


@app.post('/users')
async def post_users(users_data: UsersData):
    # проверка является ли пользователь админом
    user_id = (await verify_token(config['jwt_secret'], users_data.token)).get('as')
    await verify_admin(engine, user_id)

    async with engine.connect() as conn:
        result = await conn.execute(select(AuthUser))

    # сборка ответа
    log.info(f'returning users for {user_id}')
    return [{k: v for k, v in zip(list(result.keys()), row)} for row in result]
