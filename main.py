#!/usr/bin/env python

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import pandas as pd
import asyncpg

import os


data = {}

with open('pages/index.html') as f:
    index_html = f.read()
with open('pages/owners.html') as f:
    owners_html = f.read()
with open('pages/animals.html') as f:
    animals_html = f.read()

app = FastAPI()


async def client_animals_query(aid='', owner='', breed='', sex='', birthday='', reg_date='', description=''):
    query = (
        '''
        SELECT
            animals.id, owners.last_name || ' ' || owners.name || ' ' || owners.middle_name,
            animals.nick, animals.breed,
            CASE
                WHEN animals.sex = true THEN 'Ж'
                ELSE 'М'
            END AS sex, animals.birthday,
            animals.reg_date, animals.description
        FROM
            animals LEFT JOIN owners ON animals.owner = owners.id
        '''
    )

    frame = pd.DataFrame(await data['connection'].fetch(query))
    frame.columns = ['ID', 'ФИО Владельца', 'Кличка', 'Тип', 'Пол', 'Дата рождения', 'Дата регистрации', 'Описание']

    return frame


async def client_owners_query(oid='', name='', last_name='', middle_name='', sex='', birthday='', home=''):
    query = (
        '''
        SELECT
            id, name, last_name, middle_name,
            CASE
                WHEN owners.sex = true THEN 'Ж'
                ELSE 'М'
            END AS sex, birthday, home
        FROM
            owners
        '''
    )

    frame = pd.DataFrame(await data['connection'].fetch(query))
    frame.columns = ['ID', 'Имя', 'Фамилия', 'Отчество', 'Пол', 'Дата рождения', 'Номер дома']

    return frame


@app.on_event('startup')
async def startup():
    data['connection'] = await asyncpg.connect(host=os.getenv('DHOST'), port=os.getenv('DPORT'), user=os.getenv('DUSER'), database=os.getenv('DNAME'))


@app.get('/', response_class=HTMLResponse)
async def index():
    return index_html


@app.get('/owners', response_class=HTMLResponse)
async def owners(oid='', name='', last_name='', middle_name='', sex='', birthday='', home=''):
    frame = await client_owners_query(oid, name, last_name, middle_name, sex, birthday, home)
    return owners_html.replace('TABLE_DATA', frame.to_html(index=False, justify='center'))


@app.get('/animals', response_class=HTMLResponse)
async def animals(aid='', owner='', breed='', sex='', birthday='', reg_date='', description=''):
    frame = await client_animals_query(aid, owner, breed, sex, birthday, reg_date, description)
    return animals_html.replace('TABLE_DATA', frame.to_html(index=False, justify='center'))

