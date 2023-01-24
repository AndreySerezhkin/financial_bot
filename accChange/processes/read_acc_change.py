from aiogram import types, Dispatcher

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import accChange.keyboards as keyboards
from common_modules.common_objects import bot
from common_modules.common_handlers import to_start, cancel_process
from accChange.services import AccChange


class FSMReadingAccChange(StatesGroup):
    action= State()

async def read_fsm_acc_change(user_id: types.base.Integer, acc_change: list):
    await FSMReadingAccChange.action.set()

    await bot.send_message(user_id,
                           f"""{acc_change['type_change']}: {acc_change['amount']:.2f}
                                            Категория: '{acc_change['cat_name']}'
                                            Счёт: '{acc_change['bill_name']}'
                                            
                                            Что дальше?"""
                                            .replace("  ", "").replace("\n ", "\n"),
                           reply_markup=keyboards.kb_choose_act)
    

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


def reg_processes_acc_change_read(dp: Dispatcher):
    dp.register_message_handler(read_fsm_acc_change, state=None)
    dp.register_message_handler(cancel_change, regexp='Отмена', state='*')
    dp.register_message_handler(choose_action, state=FSMReadingAccChange.action)
    
