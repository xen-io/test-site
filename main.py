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


@app.on_event('startup')
async def startup():
    data['connection'] = await asyncpg.connect(host=os.getenv('DHOST'), port=os.getenv('DPORT'), user=os.getenv('DUSER'), database=os.getenv('DNAME'))


@app.get('/', response_class=HTMLResponse)
async def index():
    return index_html


@app.get('/owners', response_class=HTMLResponse)
async def owners():
    frame: pd.DataFrame = pd.DataFrame(await data['connection'].fetch('SELECT * FROM owners'))
    frame.columns = ['ID', 'Имя', 'Фамилия', 'Отчество', 'Пол', 'Дата рождения', 'Номер дома']
    return owners_html.replace('TABLE_DATA', frame.to_html(index=False, justify='center'))


@app.get('/animals', response_class=HTMLResponse)
async def animals():
    frame: pd.DataFrame = pd.DataFrame(await data['connection'].fetch('SELECT * FROM animals'))
    frame.columns = ['ID', 'ID Владельца', 'Кличка', 'Тип', 'Пол', 'Дата рождения', 'Дата регистрации', 'Описание']
    return animals_html.replace('TABLE_DATA', frame.to_html(index=False, justify='center'))
