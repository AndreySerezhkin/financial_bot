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


class FSMReadingAccChange(StatesGroup):
    type = State()
    date_read = State()
    action= State()

async def show_fsm_acc_change(user_id, acc_change):
    await FSMReadingAccChange.action.set()

    await bot.send_message(f"""{acc_change['type_change']}: {acc_change['amount']:.2f}
                                            Категория: '{acc_change['cat_name']}'
                                            Счёт: '{acc_change['bill_name']}'
                                            
                                            Что дальше?"""
                                            .replace("  ", "").replace("\n ", "\n"),
                                        reply_markup=acc_change_kb.kb_choose_act)

    await (user_id, f"""Запись удалена.\nЧто дальше""", reply_markup=acc_change_kb.kb_choose_act)


def reg_processes_acc_change_read(dp: Dispatcher):
    dp.register_message_handler(show_fsm_acc_change, state=None)
    dp.register_message_handler(cancel_create, regexp='Отмена', state='*')
    dp.register_message_handler(set_type, state=FSMReadingAccChange.type)
    dp.register_message_handler(choose_action, state=FSMReadingAccChange.action)

# async with state.proxy() as data:
    #     data['date'] = result['record_date']
    #     kb_choose_action = acc_change_kb.generate_action_kb(result['type'])
    #     await callback_query.message.answer(f"""{type_change}: {amount:.2f}
    #                                             Категория: '{result['cat_name']}'
    #                                             Счёт: '{result['bill_name']}'"""
    #                                             .replace("  ", "").replace("\n ", "\n"),
    #                                         reply_markup=kb_choose_action)

# class FSMReadingAccChange(StatesGroup):
#     type = State()
#     date_read = State()
#     action= State()

# async def show_fsm_acc_change(message: types.Message):
#     await FSMReadingAccChange.date_read.set()
#     await message.answer("Выбери дату:", reply_markup=await DialogCalendar().start_calendar())


# # dialog calendar usage
# @dp.callback_query_handler(dialog_cal_callback.filter(), state=FSMReadingAccChange.date_read)
# async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
#     selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
#     if selected:
#         await FSMReadingAccChange.type.set()
#         # state = Dispatcher.get_current().current_state()
#         async with state.proxy() as data:
#             data['date'] = date
#             await callback_query.message.answer('Что будем смотреть?', reply_markup=acc_change_kb.kb_acc_change)


# async def cancel_create(message: types.Message, state: FSMContext):
#     await common_handlers.cancel_process(message=message, state=state)


# async def set_type(message: types.Message, state: FSMContext):

#     async with state.proxy() as data:
#         if 'Расход' in message.text and 'type' not in data:
#             data['type'] = 'e'
#         elif 'Доход' in message.text and 'type' not in data:
#             data['type'] = 'i'

#         data['type_name'] = message.text
            
#     with Postgres() as (conn, cursor):
#         cursor.execute(f""" SELECT *
#                               FROM acc_change
#                               WHERE user_id = {message.from_user.id}
#                                 AND type = '{data['type']}'
#                                 AND record_date = '{data['date'].strftime("%Y-%m-%d")}';""")
        
#         result = cursor.fetchall()

#         cursor.execute(f""" SELECT bill_id, bill_name
#                             FROM bill
#                             WHERE user_id = {message.from_user.id};""")

#         bills = cursor.fetchall()

#         cursor.execute(f""" SELECT cat_id, cat_name
#                                 FROM category
#                                 WHERE user_id = {message.from_user.id};""")

#         categories = cursor.fetchall()

#     bill_dict = {}
#     for bill in bills:
#         bill_dict[bill['bill_id']] = bill['bill_name']

#     category_dict = {}
#     for category in categories:
#         category_dict[category['cat_id']] = category['cat_name']

#     logger.info(f'{bill_dict}\n{category_dict}') 
#     acc_changes = {}
#     for row in result:
#         logger.info(f'{row}')
#         acc_changes[f'acc{row["acc_change_id"]}'] = f"""{(row['amount'] / 100):.2f}\n'{category_dict[row['cat_id']]}'"""
        
#     kb_acc_changes = common_kb.generate_entity_btn_inline(acc_changes)
#     await state.finish()
#     await bot.send_message(message.from_user.id, f"""{data['type_name']} за {data['date'].strftime("%d.%m.%Y")}""", reply_markup=kb_acc_changes)
    


# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('acc'))
# async def output_acc(callback_query: types.CallbackQuery):
#     acc_change_id = int(callback_query.data.replace('acc', ''))
#     logger.info(f'{acc_change_id}, {callback_query.from_user.id}')
#     with Postgres() as (conn, cursor):
#         cursor.execute(f""" SELECT *
#                             FROM acc_change
#                             WHERE user_id = {callback_query.from_user.id}
#                                 AND acc_change_id = {acc_change_id};""")

#         result = cursor.fetchall()[0]

#         logger.info(f'result = {result}')

#         cursor.execute(f""" SELECT bill_id, bill_name
#                             FROM bill
#                             WHERE user_id = {callback_query.from_user.id}
#                               AND bill_id = {result['bill_id']};""")

#         bill = cursor.fetchall()[0]

#         cursor.execute(f""" SELECT cat_id, cat_name
#                                 FROM category
#                                 WHERE user_id = {callback_query.from_user.id}
#                                   AND cat_id = {result['cat_id']};""")

#         category = cursor.fetchall()[0]

#     if result['type'] == 'e':
#         type_change = 'Расход'
#     else:
#         type_change = 'Доход'

#     amount = float(result['amount'] / 100)

#     await FSMReadingAccChange.action.set()
#     state = Dispatcher.get_current().current_state()
#     async with state.proxy() as data:
#         data['date'] = result['record_date']
#         kb_choose_action = acc_change_kb.generate_action_kb(result['type'])
#         await callback_query.message.answer(f"""{type_change}: {amount:.2f}
#                                                 Категория: '{category['cat_name']}'
#                                                 Счёт: '{bill['bill_name']}'"""
#                                                 .replace("  ", "").replace("\n ", "\n"),
#                                             reply_markup=kb_choose_action)


# async def choose_action(message: types.Message, state: FSMContext):
    
#     if 'Расход' in message.text or 'Доход' in message.text:
#         await set_type(message, state)
    
#     elif message.text == 'Другая дата':
#         await state.finish()
#         await read_fsm_acc_change(message)

#     elif message.text == 'В начало':
#         await common_handlers.to_start(message, state)
    

# def reg_processes_acc_change_read(dp: Dispatcher):
#     dp.register_message_handler(read_fsm_acc_change, state=None)
#     dp.register_message_handler(cancel_create, regexp='Отмена', state='*')
#     dp.register_message_handler(set_type, state=FSMReadingAccChange.type)
#     dp.register_message_handler(choose_action, state=FSMReadingAccChange.action)
