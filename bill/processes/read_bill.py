from aiogram import types, Dispatcher

from common_modules.common_objects import bot
from bill.keyboards import kb_action_bill
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from common_modules import common_handlers
from . import change_bill
from bill.services import Bill


class FSMReadingBill(StatesGroup):
    bill_name = State()
    action = State()


async def read_fsm_bill(message: types.Message):
    await Bill.send_user_bills_names(bot, message, FSMReadingBill.bill_name, 'Какой счёт посмотрим?')

async def cancel_read_bill(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message=message, state=state)


async def choose_bill(message: types.Message, state: FSMContext):

    result = await Bill.get_bill(message)

    async with state.proxy() as data:
        data['bill_name'] = result["bill_name"]

    await FSMReadingBill.next()
    await bot.send_message(message.from_user.id,
                           (f"""Название: {result["bill_name"]}
                            Баланс: {result["acc_balance"]/100:.2f}
                            {result["is_calc_text"]}""".replace("  ", "")),
                           reply_markup=kb_action_bill)


async def choose_action(message: types.Message, state: FSMContext):
    
    if message.text == 'Изменить':
        async with state.proxy() as data:
            message.text = data["bill_name"]

        await change_bill.FSMChangingBill.bill_name.set()
        await change_bill.choose_bill(message, state)

    elif message.text == 'В начало':
        await common_handlers.to_start(message, state)


def reg_processes_bill_read(dp: Dispatcher):
    """Регистрация событий"""

    dp.register_message_handler(read_fsm_bill, state=None)
    dp.register_message_handler(cancel_read_bill, regexp='Отмена', state='*')
    dp.register_message_handler(choose_bill, state=FSMReadingBill.bill_name)
    dp.register_message_handler(choose_action, state=FSMReadingBill.action)
