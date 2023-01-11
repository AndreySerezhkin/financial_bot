from aiogram import types, Dispatcher
from loguru import logger

from common_obj import bot
from keyboards import kb_action_bill_del
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.Postgres import Postgres
from processes import common_handlers
from entity.Category.Category import Category


class FSMDeletingCat(StatesGroup):
    cat_name = State()
    action = State()


async def delete_fsm_cat(message: types.Message):
    await Category.get_all_user_cats(bot, message, FSMDeletingCat.cat_name, 'Какую категорию удалим?', True)


async def cancel_delete_cat(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message, state)


async def delete_cat(message: types.Message, state: FSMContext):

    with Postgres() as (conn, cursor):
        cursor.execute(f""" DELETE FROM category
                            WHERE cat_name = '{message.text}'
                                AND user_id = {message.from_user.id};""")

        logger.info(f'deleted category: {message.text} from user {message.from_user.id}')

    await FSMDeletingCat.next()
    await bot.send_message(message.from_user.id, 
                           'Готово! Что дальше?',
                           reply_markup=kb_action_bill_del)


async def choose_action(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Удалить еще':
        await delete_fsm_cat(message)
    elif message.text == 'В начало':
        await common_handlers.to_start(message, state)


def reg_processes_cat_delete(dp: Dispatcher):
    dp.register_message_handler(delete_fsm_cat, state=None)
    dp.register_message_handler(cancel_delete_cat, regexp='Отмена', state='*')
    dp.register_message_handler(delete_cat, state=FSMDeletingCat.cat_name)
    dp.register_message_handler(choose_action, state=FSMDeletingCat.action)