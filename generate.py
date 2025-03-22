#!/usr/bin/env python

from faker import Faker
import random

import asyncio
import asyncpg

import os


fake = Faker('ru_RU')


def gen_owner():
    sex = random.randint(0, 1)
    return {
        'name': fake.first_name_female() if sex else fake.first_name_male(),
        'last_name': fake.last_name_female() if sex else fake.last_name_male(),
        'middle_name': fake.middle_name_female() if sex else fake.middle_name_male(),
        'sex': 'true' if sex else 'false',
        'birthday': fake.date_of_birth(minimum_age=21, maximum_age=67).strftime('%d.%m.%Y'),
        'home': random.randint(1, 145)
    }


def gen_animal(owner_id):
    sex = random.randint(0, 1)
    birthday = fake.date_of_birth(minimum_age=1, maximum_age=10)
    return {
        'owner_id': owner_id,
        'animal_nick': fake.first_name_female() if sex else fake.first_name_male(),
        'animal_type': random.choice(['Собака', 'Корова', 'Кот', 'Свинья', 'Курица', 'Козел']),
        'animal_sex': 'true' if sex else 'false',
        'animal_birthday': birthday.strftime('%d.%m.%Y'),
        'animal_reg_date': fake.date_time_between(start_date=birthday).strftime('%d.%m.%Y %H:%M:%S'),
        'animal_description': fake.text(50)
    }


async def gen_owners(conn, owner_count):
    for _ in range(owner_count):
        owner = list(gen_owner().values())
        await conn.execute('INSERT INTO owners (owner_name, owner_lastname, owner_middlename, owner_sex, owner_birthday, owner_home) VALUES (\'{}\', \'{}\', \'{}\', {}, \'{}\', {});'.format(*owner))


async def gen_animals(conn, owner_count, animal_count):
    for i in range(animal_count):
        animal = list(gen_animal(i + 1 if i + 1 <= owner_count else random.randint(1, owner_count)).values())
        await conn.execute('''INSERT INTO animals (owner_id, animal_nick, animal_type, animal_sex, animal_birthday, animal_reg_date, animal_description) VALUES ({}, \'{}\', \'{}\', {}, \'{}\', \'{}\', \'{}\');'''.format(*animal))


async def main():
    conn = await asyncpg.connect(host=os.getenv('DHOST'), port=os.getenv('DPORT'), user=os.getenv('DUSER'), database=os.getenv('DNAME'))

    await gen_owners(conn, 30)
    await gen_animals(conn, 30, 500)

    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
