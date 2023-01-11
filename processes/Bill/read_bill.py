from aiogram import types, Dispatcher

from common_obj import bot
from keyboards import kb_action_bill
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from processes import common_handlers
from processes.Bill import change_bill
from entity.Bill.Bill import Bill


class FSMReadingBill(StatesGroup):
    bill_name = State()
    action = State()


async def read_fsm_bill(message: types.Message):
    await Bill.get_all_user_bills(bot, message, FSMReadingBill.bill_name, 'Какой счёт посмотрим?')

async def cancel_read_bill(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message=message, state=state)


async def choose_bill(message: types.Message, state: FSMContext):

    result = await Bill.get_bill(message)

    async with state.proxy() as data:
        data['bill_id'] = result["bill_id"]
        data['bill_name'] = result["bill_name"]
        data['acc_balance'] = float(result["acc_balance"] / 100)
        data['is_calc'] = result["is_calc"]

    await FSMReadingBill.next()
    await bot.send_message(message.from_user.id,
                           (f"""Название: {result["bill_name"]}
                            Баланс: {result["acc_balance"]:.2f}
                            {result["is_calc"]}""".replace("  ", "")),
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
    dp.register_message_handler(read_fsm_bill, state=None)
    dp.register_message_handler(cancel_read_bill, regexp='Отмена', state='*')
    dp.register_message_handler(choose_bill, state=FSMReadingBill.bill_name)
    dp.register_message_handler(choose_action, state=FSMReadingBill.action)
