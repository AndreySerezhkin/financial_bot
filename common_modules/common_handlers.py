from aiogram import types

from loguru import logger
from aiogram.dispatcher import FSMContext

from .common_objects import bot
from entity import entity_process
from users.services import User


async def cancel_process(message: types.Message, state: FSMContext):
    """Отмена процессв и переход в начало
       PARAMETERS:  message - последнее сообщение пользователя
                    state - состояние процесса, который отменяем 
    """

    current_state = await state.get_state()
    logger.info(f'Cancel from state "{current_state}"')

    result = User.get_user(message.from_user.id)

    await bot.send_message(message.from_user.id, 'Отменил')
    if current_state is None:
        await entity_process.start_fsm_action(message, result['user_name'])

    await state.finish()
    await entity_process.start_fsm_action(message, result['user_name'])


async def to_start(message: types.Message, state: FSMContext):
    """Переход на старт с помощью команды 'На Старт'
       с выводом сущностей для выбора 
    """

    result = User.get_user(message.from_user.id)

    await state.finish()
    await entity_process.start_fsm_action(message, result['user_name'])
