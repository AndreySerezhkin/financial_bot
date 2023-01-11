from aiogram import types, Dispatcher
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from common_obj import bot
from database.Postgres import Postgres
from processes import common_handlers
from keyboards import bill_kb, common_kb
from entity.Category.Category import Category


class FSMChangingCat(StatesGroup):
    cat_name = State()
    new_param = State()
    action = State()


async def change_fsm_cat(message: types.Message):
    await Category.get_all_user_cats(bot, message, FSMChangingCat.cat_name, 'Какую категорию изменим?', True)


async def cancel_change_cat(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message, state)


async def change_cat(message: types.Message, state: FSMContext):
    with Postgres() as (conn, cursor):
        cursor.execute(f""" SELECT *
                            FROM category
                            WHERE cat_name = '{message.text}'
                              AND user_id = {message.from_user.id};""")

        result = cursor.fetchall()[0]

    async with state.proxy() as data:
        data['cat_id'] = result['cat_id']

    await FSMChangingCat.next()
    await bot.send_message(message.from_user.id,
                           f'Введите новое название',
                           reply_markup=bill_kb.kb_params_bill)


async def set_new_param(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        cat_id = data['cat_id']
        field_value = message.text

        data['cat_name'] = field_value

    with Postgres() as (conn, cursor):
        cursor.execute(f"""UPDATE category
                           SET cat_name = '{field_value}'
                           where cat_id = {cat_id}""")

    logger.info(f'Update category field cat_name = {field_value}')

    await FSMChangingCat.next()
    await bot.send_message(message.from_user.id,
                           'Что дальше?',
                           reply_markup=bill_kb.kb_end_change_bill)


async def choose_action(message: types.Message, state: FSMContext):
    
    if message.text == 'Изменить другую категорию':
        await state.finish()
        await change_fsm_cat(message)
    elif message.text == 'В начало':
        await state.finish()
        await common_handlers.to_start(message, state)


def reg_processes_cat_change(dp: Dispatcher):
    dp.register_message_handler(change_fsm_cat, state=None)
    dp.register_message_handler(cancel_change_cat, regexp='Отмена', state='*')
    dp.register_message_handler(change_cat, state=FSMChangingCat.cat_name)
    dp.register_message_handler(set_new_param, state=FSMChangingCat.new_param)
    dp.register_message_handler(choose_action, state=FSMChangingCat.action)
