from aiogram import types, Dispatcher
from loguru import logger

from common_obj import bot
from keyboards import kb_action_bill_del
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.Postgres import Postgres
from processes import common_handlers
from entity.Bill.Bill import Bill


class FSMDeletingBill(StatesGroup):
    bill_name = State()
    action = State()


async def delete_fsm_bill(message: types.Message):
    await Bill.get_all_user_bills(bot, message, FSMDeletingBill.bill_name, 'Какой счёт удалим?')


async def cancel_delete_bill(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message, state)


async def delete_bill(message: types.Message, state: FSMContext):

    with Postgres() as (conn, cursor):
        cursor.execute(f""" DELETE FROM bill
                            WHERE bill_name = '{message.text}'
                                AND user_id = {message.from_user.id};""")

        logger.info(f'deleted bill: {message.text} from user {message.from_user.id}')

    await FSMDeletingBill.next()
    await bot.send_message(message.from_user.id, 
                           'Готово! Что дальше?',
                           reply_markup=kb_action_bill_del)


async def choose_action(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Удалить еще':
        await delete_fsm_bill(message)
    elif message.text == 'В начало':
        await common_handlers.to_start(message, state)


def reg_processes_bill_delete(dp: Dispatcher):
    dp.register_message_handler(delete_fsm_bill, state=None)
    dp.register_message_handler(cancel_delete_bill, regexp='Отмена', state='*')
    dp.register_message_handler(delete_bill, state=FSMDeletingBill.bill_name)
    dp.register_message_handler(choose_action, state=FSMDeletingBill.action)