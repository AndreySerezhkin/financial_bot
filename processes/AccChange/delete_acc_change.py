from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from database import Postgres
from common_obj import bot
from keyboards import acc_change_kb
from entity.AccChange.AccChange import AccChange


class FSMRDeletingAccChange(StatesGroup):
    action= State()


async def delete_fsm_acc_change(user_id, acc_change_id):

    await FSMRDeletingAccChange.action.set()

    with Postgres() as (conn, cursor):
        cursor.execute(f""" DELETE FROM acc_change 
                            WHERE user_id = {user_id}
                              AND acc_change_id = {acc_change_id};""")

        logger.info(f'Deleted record acc_change {acc_change_id=} and {user_id=}')


    await bot.send_message(user_id, f"""Запись удалена.\nЧто дальше""", reply_markup=acc_change_kb.kb_choose_act)


async def choose_action(message: types.Message, state: FSMContext):
    AccChange.choose_action(message, state)
    

def reg_processes_acc_change_delete(dp: Dispatcher):
    dp.register_message_handler(delete_fsm_acc_change, state=None)
    dp.register_message_handler(choose_action, state=FSMRDeletingAccChange.action)