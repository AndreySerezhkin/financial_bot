from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from common_modules.database import Postgres
from common_modules.common_objects import bot
import accChange.keyboards as keyboards
from common_modules.common_handlers import to_start, cancel_process
from accChange.services import AccChange


class FSMRDeletingAccChange(StatesGroup):
    action= State()


async def delete_fsm_acc_change(user_id, acc_change_id):

    await FSMRDeletingAccChange.action.set()

    with Postgres() as (conn, cursor):
        cursor.execute(f""" DELETE FROM acc_change 
                            WHERE user_id = {user_id}
                              AND acc_change_id = {acc_change_id};""")

        logger.info(f'Deleted record acc_change {acc_change_id=} and {user_id=}')


    await bot.send_message(user_id, f"""Запись удалена.\nЧто дальше""", reply_markup=keyboards.kb_choose_act)


async def cancel_change(message: types.Message, state: FSMContext):
    await cancel_process(message=message, state=state)


async def choose_action(message: types.Message, state: FSMContext):

    await AccChange.choose_acc_change_action(message, state)

    # if 'Расход' or 'Доход' in message.text:
    #     async with state.proxy() as data:
    #         message.text = data["bill_name"]

    #     await set_type_acc_change(message, state)

    # elif message.text == 'В начало':
    #     await to_start(message, state)

    # else:
    #     await exist_fsm_acc_change(message, action = 'change')
    

def reg_processes_acc_change_delete(dp: Dispatcher):
    dp.register_message_handler(delete_fsm_acc_change, state=None)
    dp.register_message_handler(cancel_change, regexp='Отмена', state='*')
    dp.register_message_handler(choose_action, state=FSMRDeletingAccChange.action)