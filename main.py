#!/usr/bin/env python

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import pandas as pd
import asyncpg

import os


data = {}

with open('index.html') as f:
    index_html = f.read()
with open('owners.html') as f:
    owners_html = f.read()
with open('animals.html') as f:
    animals_html = f.read()

app = FastAPI()


async def owners_frame():
    query = '''SELECT * FROM owners'''
    # ответ на запрос query засовывается в frame типа DataFrame
    frame = pd.DataFrame(await data['connection'].fetch(query))
    frame.columns = ['ID', 'Имя', 'Фамилия', 'Отчество', 'Пол', 'Дата рождения', 'Номер дома']
    # форматируется колонка Пол
    frame['Пол'] = frame['Пол'].apply(lambda x: 'Ж' if x else 'М')
    return frame


async def animals_frame():
    query = '''
    SELECT
        animal_id, CONCAT(owner_lastname, ' ', owner_name, ' ', owner_middlename),
        animal_nick, animal_type,
        animal_sex, animal_birthday,
        animal_reg_date, animal_description
    FROM
        animals LEFT JOIN owners ON animals.owner_id = owners.owner_id'''
    # ответ на запрос query засовывается в frame типа DataFrame
    frame = pd.DataFrame(await data['connection'].fetch(query))
    frame.columns = ['ID', 'ФИО Владельца', 'Кличка', 'Тип', 'Пол', 'Дата рождения', 'Дата регистрации', 'Описание']
    # форматируется колонка Пол
    frame['Пол'] = frame['Пол'].apply(lambda x: 'Ж' if x else 'М')
    return frame


@app.on_event('startup')
async def startup():
    data['connection'] = await asyncpg.connect(host=os.getenv('DHOST'), port=os.getenv('DPORT'), user=os.getenv('DUSER'), database=os.getenv('DNAME'))


@app.get('/', response_class=HTMLResponse)
async def index():
    return index_html


@app.get('/owners', response_class=HTMLResponse)
async def owners():
    return owners_html.replace('TABLE_DATA', (await owners_frame()).to_html(index=False, justify='center'))


@app.get('/animals', response_class=HTMLResponse)
async def animals():
    return animals_html.replace('TABLE_DATA', (await animals_frame()).to_html(index=False, justify='center'))
