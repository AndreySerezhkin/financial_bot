from aiogram import types, Dispatcher
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from common_obj import bot
from database.Postgres import Postgres
from processes import common_handlers
from keyboards import bill_kb, common_kb
from entity.Bill.Bill import Bill


class FSMChangingBill(StatesGroup):
    bill_name = State()
    param = State()
    new_param = State()
    action = State()


async def change_fsm_bill(message: types.Message):
    """Изменение счёта"""
    await Bill.send_user_bills_names(bot, message, FSMChangingBill.bill_name, 'Какой счёт изменим?')


async def cancel_change_bill(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message, state)


async def choose_bill(message: types.Message, state: FSMContext):
    result = await Bill.get_bill(message)

    async with state.proxy() as data:
        data['bill_id'] = result["bill_id"]
        data['bill_name'] = result["bill_name"]
        data['acc_balance'] = float(result["acc_balance"] / 100)
        data['is_calc'] = result["is_calc"]

    await FSMChangingBill.next()
    await bot.send_message(message.from_user.id,
                           f"""Название: {result["bill_name"]}
                               Баланс: {result["acc_balance"]}
                               {result["is_calc"]}\n
                               Что будем менять?""".replace('  ', '').replace('\n ','\n'),
                           reply_markup=bill_kb.kb_params_bill)


async def choose_param(message: types.Message, state: FSMContext):
    await FSMChangingBill.next()

    async with state.proxy() as data:
        data['param'] = message.text

    if message.text in ('Название', 'Баланс счёта'):
        await bot.send_message(message.from_user.id, f'Введите {message.text}')
    elif message.text == 'Учёт в общем балансе':
        await bot.send_message(message.from_user.id,
                               'Учитывать этот счёт в общем бюджете?',
                               reply_markup=common_kb.kb_close_question)


async def set_new_param(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        param = data['param']
        bill_id = data['bill_id']

        if param == 'Название':
            field = 'bill_name'
            field_value = message.text
        elif param == 'Баланс счёта':
            field = 'acc_balance'
            field_value = int(float(message.text) * 100)
        elif param == 'Учёт в общем балансе':
            field = 'is_not_calc'
            if message.text == 'Да':
                field_value = False
            else:
                field_value = True

        data[field] = field_value

    with Postgres() as (conn, cursor):
        cursor.execute(f"""UPDATE bill
                           SET {field} = '{field_value}'
                           where bill_id = {bill_id}""")

        logger.info(f'Update bill field {field} = {field_value}')

    await FSMChangingBill.next()
    await bot.send_message(message.from_user.id,
                           'Что дальше?',
                           reply_markup=bill_kb.kb_end_change_bill)


async def choose_action(message: types.Message, state: FSMContext):
    
    if message.text == 'Изменить этот же счёт':
        async with state.proxy() as data:
            logger.info(f'data: {data}')
            await FSMChangingBill.param.set()
            await bot.send_message(message.from_user.id,
                                   f"""Название: {data["bill_name"]}
                                       Баланс: {data["acc_balance"]:.2f}
                                       {data["is_calc"]}\n
                                       Что будем менять?""".replace("  ", "").replace("\n ", "\n"),
                                   reply_markup=bill_kb.kb_params_bill)
    elif message.text == 'Изменить другой счёт':
        await state.finish()
        await change_fsm_bill(message)
    elif message.text == 'В начало':
        await state.finish()
        await common_handlers.to_start(message, state)


def reg_processes_bill_change(dp: Dispatcher):
    dp.register_message_handler(change_fsm_bill, state=None)
    dp.register_message_handler(cancel_change_bill, regexp='Отмена', state='*')
    dp.register_message_handler(choose_bill, state=FSMChangingBill.bill_name)
    dp.register_message_handler(choose_param, state=FSMChangingBill.param)
    dp.register_message_handler(set_new_param, state=FSMChangingBill.new_param)
    dp.register_message_handler(choose_action, state=FSMChangingBill.action)
