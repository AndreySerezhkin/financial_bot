from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from common_obj import bot
from keyboards import kb_client, kb_action

from entity.EntityFabrica import EntityFabrica


class FSMAction(StatesGroup):
    entity = State()
    name = State()
    actions = State()


async def start_fsm_action(message: types.Message, user_name):
    """Вывод Сущностей с которыми можно работать"""

    await FSMAction.entity.set()
    await bot.send_message(message.from_user.id,
                           f'{user_name}, с чем будем работать?',
                           reply_markup=kb_client)


async def choose_entity(message: types.Message, state: FSMContext):
    """Запись выбранной сущности и вывод действий с сущностью"""

    async with state.proxy() as data:
        data['entity'] = message.text
    await FSMAction.actions.set()
    await bot.send_message(message.from_user.id,
                           'Что будем делать?',
                           reply_markup=kb_action)


async def choose_action(message: types.Message, state: FSMAction):
    """Вызов выбранного действия сущности"""

    async with state.proxy() as data:
        await EntityFabrica.create_object(data['entity'])

    await state.finish()

    await EntityFabrica.execute_process(message)


def reg_processes_client(dp: Dispatcher):
    dp.register_message_handler(choose_entity, state=FSMAction.entity)
    dp.register_message_handler(choose_action, state=FSMAction.actions)
