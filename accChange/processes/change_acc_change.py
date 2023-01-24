from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_calendar import dialog_cal_callback, DialogCalendar
from loguru import logger

import accChange.keyboards as keyboards
from common_modules.common_objects import dp, bot
from common_modules.common_handlers import to_start, cancel_process
from common_modules.database import Postgres
from accChange.services import AccChange
from bill.services import Bill
from category.services import Category



class FSMChangingAccChange(StatesGroup):
    param = State()
    date_change = State()
    new_param = State()
    action= State()


async def change_fsm_acc_change(user_id, acc_change, state):
    """Начало изменения выбранного счёта"""

    async with state.proxy() as data:
        data['acc_change_id'] = acc_change['acc_change_id']
        data['type'] = acc_change['type']
        data['user_id'] = user_id

    await FSMChangingAccChange.param.set()

    await bot.send_message(user_id,
                           f"""{acc_change['type_change']}: {acc_change['amount']:.2f}
                               Категория: '{acc_change['cat_name']}'
                               Счёт: '{acc_change['bill_name']}'
                                            
                               Что меняем?"""
                               .replace("  ", "").replace("\n ", "\n"),
                            reply_markup=keyboards.kb_choose_param)


async def cancel_change(message: types.Message, state: FSMContext):
    await cancel_process(message=message, state=state)


async def choose_param(message: types.Message, state: FSMContext):
    """В зависимости от выбранного параметра, просим пользователя ввести данные"""

    async with state.proxy() as data:
        data['param'] = message.text

    await FSMChangingAccChange.new_param.set()

    if message.text in ('Счёт'):
        await Bill.send_user_bills_names(bot=bot, 
                                         message=message, 
                                         state=FSMChangingAccChange.new_param, 
                                         text='Выберите счёт')
        
    elif message.text == 'Сумма':
        await bot.send_message(message.from_user.id, f'Введите сумму')
    
    elif message.text == 'Тип': 
        await bot.send_message(message.from_user.id, f'Укажите тип', reply_markup=keyboards.kb_acc_change)

    elif message.text == 'Дата':
        await FSMChangingAccChange.date_change.set()
        await message.answer("Выбери дату:", reply_markup=await DialogCalendar().start_calendar())

    elif message.text == 'Категория':
        await Category.get_all_user_cats(bot=bot, 
                                         message=message, 
                                         state=FSMChangingAccChange.new_param, 
                                         text='Выберите категорию',
                                         btn=True)


@dp.callback_query_handler(dialog_cal_callback.filter(), state=FSMChangingAccChange.date_change)
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем дату с помощью диалогового календаря"""
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['date'] = date

            param = data['param']
            
            field, field_value = await AccChange.fill_data_by_param(data=data, 
                                                                    param=param, 
                                                                    text='hello',
                                                                    user_id=data['user_id'])

            with Postgres() as (conn, cursor):
                cursor.execute(f"""UPDATE acc_change
                                SET {field} = '{field_value}'
                                where acc_change_id = {data['acc_change_id']}""")

                logger.info(f'Update acc_change field {field} = {field_value}')

        if field == 'type':
            kb_end_acc_change = keyboards.generate_action_kb(field_value)
        else:
            kb_end_acc_change = keyboards.generate_action_kb(data['type'])

        await FSMChangingAccChange.action.set()
        await callback_query.message.answer('Что дальше?',
                               reply_markup=kb_end_acc_change)


async def set_new_param(message: types.Message, state: FSMContext):
    """Изменение параметра счёта в таблице"""

    async with state.proxy() as data:
        param = data['param']
        acc_change_id = data['acc_change_id']

        field, field_value = await AccChange.fill_data_by_param(data=data, 
                                                                param=param, 
                                                                text=message.text,
                                                                user_id=message.from_user.id)

    with Postgres() as (conn, cursor):
        cursor.execute(f"""UPDATE acc_change
                           SET {field} = '{field_value}'
                           where acc_change_id = {acc_change_id}""")

        logger.info(f'Update acc_change field {field} = {field_value}')

    if field == 'type':
        kb_end_acc_change = keyboards.generate_action_kb(field_value)
    else:
        kb_end_acc_change = keyboards.generate_action_kb(data['type'])

    await FSMChangingAccChange.next()
    await bot.send_message(message.from_user.id,
                           'Что дальше?',
                           reply_markup=kb_end_acc_change)
    

async def choose_action(message: types.Message, state: FSMContext):

    await AccChange.choose_acc_change_action(message, state)
    

def reg_processes_acc_change_change(dp: Dispatcher):
    dp.register_message_handler(change_fsm_acc_change, state=None)
    dp.register_message_handler(cancel_change, regexp='Отмена', state='*')
    dp.register_message_handler(choose_param, state=FSMChangingAccChange.param)
    dp.register_message_handler(set_new_param, state=FSMChangingAccChange.new_param)
    dp.register_message_handler(choose_action, state=FSMChangingAccChange.action)