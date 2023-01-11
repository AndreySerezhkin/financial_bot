from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database import Postgres
from processes.AccChange import ( read_fsm_acc_change, 
                                  change_fsm_acc_change, 
                                  delete_fsm_acc_change )
from processes import common_handlers


class AccChange():

    @staticmethod
    async def choose_action(message: types.Message, state: FSMContext):

        if 'В начало' in message.text:
            await common_handlers.to_start(message, state)

        state.finish()
    
        if 'Посмотреть' in message.text:
            await read_fsm_acc_change(message)

        elif 'Изменить' in message.text:
            await change_fsm_acc_change(message)

        elif 'Удалить' in message.text:
            await delete_fsm_acc_change(message)

        elif 'Создать' in message.text:
            await delete_fsm_acc_change(message)