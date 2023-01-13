from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger
from aiogram_calendar import dialog_cal_callback, DialogCalendar

from accChange.services import AccChange
import accChange.keyboards as keyboards
from common_modules.common_objects import dp, bot
from common_modules import common_handlers
from common_modules import common_kb
from accChange.processes import change_acc_change, delete_acc_change, read_acc_change


class FSMExistAccChange(StatesGroup):
    type = State()
    date_read = State()
    info = State()
    next_action= State()


async def exist_fsm_acc_change(message: types.Message, action):
    """Записываем действие в состояние и просим выбрать дату изменения"""

    await FSMExistAccChange.date_read.set()
    state = Dispatcher.get_current().current_state()
    async with state.proxy() as data:
        data['action'] = action
    await message.answer("Выбери дату:", reply_markup=await DialogCalendar().start_calendar())


# dialog calendar usage
@dp.callback_query_handler(dialog_cal_callback.filter(), state=FSMExistAccChange.date_read)
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Запись выбранной даты изменения счёта в состояние"""

    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await FSMExistAccChange.type.set()
        async with state.proxy() as data:
            data['date'] = date
            await callback_query.message.answer('Выбери тип изменения', reply_markup=keyboards.kb_acc_change)


async def cancel_create(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message=message, state=state)


async def set_type_acc_change(message: types.Message, state: FSMContext):
    """Запись выбранного типа изменения счёта в состояние"""
    logger.info('set_type_acc_change')

    async with state.proxy() as data:
        if 'Расход' in message.text and 'type' not in data:
            data['type'] = 'e'
        elif 'Доход' in message.text and 'type' not in data:
            data['type'] = 'i'

        data['type_name'] = message.text

    acc_changes = AccChange.get_user_acc_changes(user_id=message.from_user.id, 
                                                 acc_change_type=data['type'], 
                                                 record_date=data['date'])
        
    kb_acc_changes = common_kb.generate_entity_btn_inline(acc_changes)
    await FSMExistAccChange.info.set()

    await bot.send_message(message.from_user.id, 
                           f"""{data['type_name']} за {data['date'].strftime("%d.%m.%Y")}""", 
                           reply_markup=kb_acc_changes)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('acc'), state=FSMExistAccChange.info)
async def output_acc(callback_query: types.CallbackQuery, state: FSMContext):
    """Передача инфо о выбранном изменении счёта действию, которое выбрали вначале(read, change, delete)"""

    acc_change_id = int(callback_query.data.replace('acc', ''))

    acc_change_info = AccChange.get_acc_change_info(user_id=callback_query.from_user.id,
                                           acc_change_id=acc_change_id)

    if acc_change_info['type'] == 'e':
        acc_change_info['type_change'] = 'Расход'
    else:
        acc_change_info['type_change'] = 'Доход'

    acc_change_info['amount'] = float(acc_change_info['amount'] / 100)

    await FSMExistAccChange.next_action.set()

    async with state.proxy() as data:
        if 'read' in data['action']:
            await read_acc_change.read_fsm_acc_change(callback_query.from_user.id, acc_change_info)

        elif 'change' in data['action']:
            await change_acc_change.change_fsm_acc_change(callback_query.from_user.id, acc_change_info)

        elif 'delete' in data['action']:
            await delete_acc_change.delete_fsm_acc_change(callback_query.from_user.id, acc_change_id)

def reg_processes_acc_change_exist(dp: Dispatcher):
    dp.register_message_handler(exist_fsm_acc_change, state=None)
    dp.register_message_handler(cancel_create, regexp='Отмена', state='*')
    dp.register_message_handler(set_type_acc_change, state=FSMExistAccChange.type)
