#!/usr/bin/env python

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import pandas as pd
import asyncpg

from string import Template
import time
import os


data = {}

with open('pages/index.html') as f:
    index_html = Template(f.read())
with open('pages/owners.html') as f:
    owners_html = Template(f.read())
with open('pages/animals.html') as f:
    animals_html = Template(f.read())

app = FastAPI()


# TODO:
# - привести даты и время в нормальный формат
# - добавить проверки на варианты пунктов для выпадающих списков
# - сделать поиск по типу животного через выпадающий список
# - зерефакторить часть кода с созданием запроса улучшить часть кода оптимизировать
#   - подстановку получше сделать (возможно через Template)
# - хотя бы как нибудь избавится от sql injection уязвимости
# - добавить проверки на формат ввода пользователя (даты и времени)


async def client_animals_query(query):
    ''' Выполняет sql запрос в таблицу animals и возвращает pd.DataFrame'''

    sql_query = (
        '''
        SELECT
            animals.id, owners.last_name || ' ' || owners.name || ' ' || owners.middle_name AS fio,
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
    # есть разделение на sql_query и sql_conditions для дальнейших запросов на получение вариантов для выпадающих списков
    sql_conditions = ' WHERE '

    # SQL INJECTION BOIIIIII
    if query['aid']:
        sql_conditions += f' (animals.id = {query["aid"]}) AND '
    if query['breed']:
        sql_conditions += f' (UPPER(animals.breed) = REPLACE(UPPER(\'{query["breed"]}\'), \' \', \'\')) AND '

    if query['owner']:
        sql_conditions += f'(UPPER(owners.last_name || \' \' || owners.name || \' \' || owners.middle_name) LIKE REPLACE(UPPER(\'%{query["owner"]}%\'), \' \', \'\')) AND '

    if query['nick']:
        sql_conditions += f' (UPPER(animals.nick) = REPLACE(UPPER(\'{query["nick"]}\'), \' \', \'\')) AND '

    if query['sex'] == '1':
        sql_conditions += ' (animals.sex = true) AND '
    elif query['sex'] == '0':
        sql_conditions += ' (animals.sex = false) AND '

    if query['birthday']:
        sql_conditions += f'(animals.birthday = DATE(\'{query["birthday"]}\')) AND '

    if query['reg_date']:
        sql_conditions += f'(animals.reg_date = TIMESTAMP(\'{query["reg_date"]}\')) AND '

    if query['description']:
        sql_conditions += f'(UPPER(animals.description) LIKE REPLACE(UPPER(\'%{query["description"]}%\'), \' \', \'\')) AND '

    sql_conditions = sql_conditions.rstrip(' AND ').rstrip(' WHERE ')

    # доп функционал для отображения query time на каждой странице с запросами
    before = time.time()
    frame = pd.DataFrame(await data['connection'].fetch(sql_query + sql_conditions))
    query['_time'] = time.time() - before

    # когда ничего по запросу не находится таблица становится размером 0x0, а frame.columns ругается на присвоение такой таблицы 8 имен колонок
    if len(frame.columns == 8):
        frame.columns = ['ID', 'ФИО Владельца', 'Кличка', 'Тип', 'Пол', 'Дата рождения', 'Дата регистрации', 'Описание']

    return frame


async def client_owners_query(query):
    ''' Выполняет sql запрос в таблицу owners и возвращает pd.DataFrame'''

    sql_query = (
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

    sql_query += ' WHERE '

    if query['oid']:
        sql_query += f' (id = \'{query["oid"]}\') AND '

    if query['name']:
        sql_query += f' (name LIKE \'%{query["name"]}%\') AND '

    if query['last_name']:
        sql_query += f' (last_name LIKE \'%{query["last_name"]}%\') AND '

    if query['middle_name']:
        sql_query += f' (middle_name LIKE \'%{query["middle_name"]}%\') AND '

    if query['sex'] == '1':
        sql_query += ' (sex = true) AND '
    elif query['sex'] == '0':
        sql_query += ' (sex = false) AND '

    if query['birthday']:
        sql_query += f'(birthday = DATE(\'{query["birthday"]}\')) AND '

    if query['home']:
        sql_query += f' (home = \'{query["home"]}\') AND '

    sql_query = sql_query.rstrip(' AND ').rstrip(' WHERE ')

    before = time.time()
    frame = pd.DataFrame(await data['connection'].fetch(sql_query))
    query['_time'] = time.time() - before

    if len(frame.columns == 7):
        frame.columns = ['ID', 'Имя', 'Фамилия', 'Отчество', 'Пол', 'Дата рождения', 'Номер дома']

    return frame


def sub_option_vals(template, input, options, prefix):
    ''' Функция выставляет selected опцию в теге option в зависимости от выбранного значения ранее '''
    vals = options[:]
    if input in vals:
        template = Template(template.safe_substitute({f'{prefix}_{input}_SELECT': 'selected'}))  # .replace(f'{prefix}_{input}_SELECT', 'selected')
        vals.remove(input)
    return Template(template.safe_substitute({f'{prefix}_{v}_SELECT': '' for v in vals}))


def owners_sub_vals(query, table):
    ''' Функция заполняет опции value в тегах для страницы /owners для удобного взаимодействия с базой '''

    # костыль для сообщения о том, что ничего не было найдено
    if '<td>' not in table:
        table = '<div><p>Nothing was found<p><div>'

    out = Template(owners_html.safe_substitute({
        'ID_VALUE': query['oid'],
        'MIDDLE_NAME_VALUE': query['middle_name'],
        'LAST_NAME_VALUE': query['last_name'],
        'NAME_VALUE': query['name'],
        'BIRTHDAY_VALUE': query['birthday'],
        'HOME_VALUE': query['home'],
        'QUERY_INFO': f'query time: {query["_time"]:.20f} sec',
        'TABLE_DATA': table
    }))
    # TODO: может потом написать функцию обертку для подобного рода страниц с таблицой и фильтрами
    out = sub_option_vals(out, query['sex'], ['-1', '0', '1'], 'SEX')
    return out.safe_substitute()


def animals_sub_vals(query, table):
    ''' Функция заполняет опции value в тегах для страницы /animals для удобного взаимодействия с базой '''

    if '<td>' not in table:
        table = '<div><p>Nothing was found<p><div>'

    out = Template(animals_html.safe_substitute({
        'ID_VALUE': query['aid'],
        'OWNER_VALUE': query['owner'],
        'NICK_VALUE': query['nick'],
        'BREED_VALUE': query['breed'],
        'BIRTHDAY_VALUE': query['birthday'],
        'REG_DATE_VALUE': query['reg_date'],
        'DESC_VALUE': query['description'],
        'QUERY_INFO': f'query time: {query["_time"]:.20f} sec',
        'TABLE_DATA': table
    }))
    out = sub_option_vals(out, query['sex'], ['-1', '0', '1'], 'SEX')
    return out.safe_substitute()


@app.on_event('startup')
async def startup():
    data['connection'] = await asyncpg.connect(host=os.getenv('DHOST'), port=os.getenv('DPORT'), user=os.getenv('DUSER'), database=os.getenv('DNAME'))


@app.get('/', response_class=HTMLResponse)
async def index():
    return index_html.safe_substitute()


@app.get('/owners', response_class=HTMLResponse)
async def owners(oid='', name='', last_name='', middle_name='', sex='', birthday='', home=''):
    # формируется словарь, т.к. довольно часто значения в нем передаются вместе
    query = {
        'oid': oid,
        'name': name,
        'last_name': last_name,
        'middle_name': middle_name,
        'sex': sex,
        'birthday': birthday,
        'home': home
    }
    frame = await client_owners_query(query)
    return owners_sub_vals(query, frame.to_html(index=False, justify='center'))


@app.get('/animals', response_class=HTMLResponse)
async def animals(aid='', owner='', nick='', breed='', sex='', birthday='', reg_date='', description=''):
    query = {
        'aid': aid,
        'owner': owner,
        'nick': nick,
        'breed': breed,
        'sex': sex,
        'birthday': birthday,
        'reg_date': reg_date,
        'description': description
    }
    frame = await client_animals_query(query)
    return animals_sub_vals(query, frame.to_html(index=False, justify='center'))
