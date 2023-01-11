from xmlrpc.client import boolean
from aiogram import types
from loguru import logger

from database import Postgres
from processes.Category import create_category
from keyboards.common_kb import generate_entity_btn ,kb_to_start


class Category():

    @staticmethod
    async def create_cat_from_oth_proc(bot, message: types.Message):
        await bot.send_message(message.from_user.id,
                               ' '.join('''Пока нет доступных категорий(. 
                                           Давайте создадим, 
                                           а потом делайте с ними что хотите'''.split()))
        await create_category.create_fsm_cat(message)

    @staticmethod
    async def write_name(message: types.Message):

        with Postgres() as (con, cursor):
            query = f""" SELECT *
                         FROM category
                         WHERE (user_id = {message.from_user.id} or user_id = 1);"""
            cursor.execute(query)

            result = cursor.fetchall()

        cancel = False
        cat_id = 0

        for row in result:
            if row['user_id'] == message.from_user.id and cat_id < row['cat_id']:
                cat_id = row['cat_id']
            if row['cat_name'] == message.text:
                cancel = True

        return {'cancel': cancel, 'cat_id': cat_id}

    @staticmethod
    async def get_all_user_cats(bot, message: types.Message, state, text: str, btn=False):
        with Postgres() as (conn, cursor):
            cursor.execute(f""" SELECT *
                                FROM category
                                WHERE user_id = {message.from_user.id};""")

            result = cursor.fetchall()

        logger.info(f'Select from user cats: {result}')

        cats = [x['cat_name']+ '\n' for x in result]

        cat_names = ''

        for name in cats:
            cat_names += f'{name}'

        if len(cats) > 0 and btn == False:

            await state.set()
            await bot.send_message(message.from_user.id,
                                   f'{text}\n{cat_names}',
                                   reply_markup=kb_to_start)

        elif len(cats) > 0 and btn == True:
            kb_read_cat = generate_entity_btn(cats, 3)

            await state.set()
            await bot.send_message(message.from_user.id,
                                   text,
                                   reply_markup=kb_read_cat)
        else:
            await Category.create_cat_from_oth_proc(bot, message)