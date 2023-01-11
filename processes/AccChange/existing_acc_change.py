from ast import If
from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger
from aiogram_calendar import dialog_cal_callback, DialogCalendar
from decimal import Decimal

from database import Postgres
from common_obj import dp, bot
from processes import common_handlers
from keyboards import acc_change_kb, common_kb
from processes.AccChange import change_acc_change, create_acc_change, delete_acc_change, read_acc_change


class FSMExistAccChange(StatesGroup):
    type = State()
    date_read = State()
    info = State()
    next_action= State()


async def read_fsm_acc_change(message: types.Message, action):

    await FSMExistAccChange.date_read.set()
    state = Dispatcher.get_current().current_state()
    async with state.proxy() as data:
        data['action'] = action
    await message.answer("Выбери дату:", reply_markup=await DialogCalendar().start_calendar())


# dialog calendar usage
@dp.callback_query_handler(dialog_cal_callback.filter(), state=FSMExistAccChange.date_read)
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):

    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await FSMExistAccChange.type.set()
        async with state.proxy() as data:
            data['date'] = date
            await callback_query.message.answer('Выбери тип изменения', reply_markup=acc_change_kb.kb_acc_change)


async def cancel_create(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message=message, state=state)


async def set_type(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        if 'Расход' in message.text and 'type' not in data:
            data['type'] = 'e'
        elif 'Доход' in message.text and 'type' not in data:
            data['type'] = 'i'

        data['type_name'] = message.text
            
    with Postgres() as (conn, cursor):
        cursor.execute(f""" SELECT acc_change.acc_change_id,
                                   acc_change.amount,
                                   category.cat_name
                              FROM acc_change
                              INNER JOIN category ON category.user_id = acc_change.user_id
                                                 AND category.cat_id = acc_change.cat_id
                              WHERE acc_change.user_id = {message.from_user.id}
                                AND acc_change.type = '{data['type']}'
                                AND acc_change.record_date = '{data['date'].strftime("%Y-%m-%d")}';""")
        
        result = cursor.fetchall()

    logger.info(f'{result}') 

    acc_changes = {}
    for row in result:
        logger.info(f'{row}')
        acc_changes[f'acc{row["acc_change_id"]}'] = f"""{(row['amount'] / 100):.2f}\n'{row['cat_name']}'"""
        
    kb_acc_changes = common_kb.generate_entity_btn_inline(acc_changes)
    await FSMExistAccChange.info.set()
    await bot.send_message(message.from_user.id, f"""{data['type_name']} за {data['date'].strftime("%d.%m.%Y")}""", reply_markup=kb_acc_changes)
    


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('acc'), state=FSMExistAccChange.info)
async def output_acc(callback_query: types.CallbackQuery, state: FSMContext):

    acc_change_id = int(callback_query.data.replace('acc', ''))

    with Postgres() as (conn, cursor):
        cursor.execute(f""" SELECT acc_change.acc_change_id,
                                   acc_change.amount,
                                   acc_change.type,
                                   acc_change.record_date,
                                   category.cat_name,
                                   bill.bill_name
                              FROM acc_change AS acc

                              INNER JOIN category ON category.user_id = acc_change.user_id
                                                 AND category.cat_id = acc_change.cat_id

                              INNER JOIN bill ON bill.user_id = acc.user_id
                                             AND bill.bill_id = acc.bill_id

                              WHERE acc_change.user_id = {callback_query.from_user.id}
                                AND acc_change.acc_change_id = {acc_change_id};""")

        result = cursor.fetchall()[0]

        logger.info(f'{result}')

    if result['type'] == 'e':
        result['type_change'] = 'Расход'
    else:
        result['type_change'] = 'Доход'

    result['amount'] = float(result['amount'] / 100)

    await FSMExistAccChange.next_action.set()

    async with state.proxy() as data:
        if 'read' in data['action']:
            await read_acc_change.show_fsm_acc_change(callback_query.from_user.id, result)

        elif 'change' in data['action']:
            await change_acc_change.change_fsm_acc_change(callback_query.from_user.id)

        elif 'delete' in data['action']:
            await delete_acc_change.delete_fsm_acc_change(callback_query.from_user.id, acc_change_id)

    # async with state.proxy() as data:
    #     data['date'] = result['record_date']
    #     kb_choose_action = acc_change_kb.generate_action_kb(result['type'])
    #     await callback_query.message.answer(f"""{type_change}: {amount:.2f}
    #                                             Категория: '{result['cat_name']}'
    #                                             Счёт: '{result['bill_name']}'"""
    #                                             .replace("  ", "").replace("\n ", "\n"),
    #                                         reply_markup=kb_choose_action)

def reg_processes_acc_change_read(dp: Dispatcher):
    dp.register_message_handler(read_fsm_acc_change, state=None)
    dp.register_message_handler(cancel_create, regexp='Отмена', state='*')
    dp.register_message_handler(set_type, state=FSMExistAccChange.type)
