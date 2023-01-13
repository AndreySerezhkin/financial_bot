from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from common_modules.common_objects import bot
from common_modules.database import Postgres, db
from common_modules import common_handlers
from common_modules import common_kb
from bill.services import Bill


class FSMCreationBill(StatesGroup):
    bill_name = State()
    acc_balance = State()
    is_not_calc = State()


async def create_fsm_bill(message: types.Message):
    """Начало процесса создания счёта, спрашиваем название"""
    await FSMCreationBill.bill_name.set()
    await bot.send_message(message.from_user.id,
                           'Название счета',
                           reply_markup=common_kb.kb_cancel)


async def cancel_create(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message=message, state=state)


async def write_name(message: types.Message, state: FSMContext):
    """Запись уникального названия счёта"""

    user_bills = await Bill.get_user_bills(user_id=message.from_user.id)

    if Bill.check_exist_users_bill(user_bills=user_bills, bill_name=message.text):
        await bot.send_message(message.from_user.id,
                               'Счёт с таким именем уже существует')
        await state.finish()
        await create_fsm_bill(message)
    else:
        async with state.proxy() as data:
            data['bill_name'] = message.text
            data['bill_id'] = Bill.get_next_new_bill_id(user_bills=user_bills)

        await FSMCreationBill.next()

        await bot.send_message(message.from_user.id,
                               'Сколько денег на счете?',
                               reply_markup=common_kb.kb_cancel)


async def write_accbalance(message: types.Message, state: FSMContext):
    """Запись баланса для нового счёта"""

    async with state.proxy() as data:
        data['acc_balance'] = int(float(message.text) * 100)

    await FSMCreationBill.next()

    await bot.send_message(message.from_user.id,
                           'Учитывать этот счёт в общем бюджете?',
                           reply_markup=common_kb.kb_close_question)


async def write_isnotcalc(message: types.Message, state: FSMContext):
    """Запись учёта счёта в общем балансе"""

    not_calc = False if message.text == 'Да' else True

    async with state.proxy() as data:

        with Postgres() as (conn, cursor):
            db.insert('bill', {'bill_name': data['bill_name'],
                            'bill_id': data['bill_id'],
                            'acc_balance': data['acc_balance'],
                            'is_not_calc': not_calc,
                            'user_id': message.from_user.id},
                    cursor=cursor, conn=conn)

            await bot.send_message(message.from_user.id,
                                f"Готово! Счёт '{data['bill_name']}' создан")

    await common_handlers.to_start(message=message, state=state)


def reg_processes_bill_create(dp: Dispatcher):
    """Регистрация событий"""

    dp.register_message_handler(create_fsm_bill, state=None)
    dp.register_message_handler(cancel_create, regexp='Отмена', state='*')
    dp.register_message_handler(write_name, state=FSMCreationBill.bill_name)
    dp.register_message_handler(write_accbalance,
                                state=FSMCreationBill.acc_balance)
    dp.register_message_handler(write_isnotcalc,
                                state=FSMCreationBill.is_not_calc)
