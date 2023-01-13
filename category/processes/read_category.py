from aiogram import types, Dispatcher

from common_modules.common_objects import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from common_modules import common_handlers
from category.services import Category
from . import create_category


class FSMReadingCats(StatesGroup):
    cat = State()


async def read_fsm_cats(message: types.Message):
    exist_category = await Category.get_all_user_cats(bot, message, FSMReadingCats.cat, 'Доступные категории:')
    if exist_category == False:
        create_category.create_fsm_cat(message)


async def to_start(message: types.Message, state: FSMContext):
    await common_handlers.to_start(message, state)


def reg_processes_cats_read(dp: Dispatcher):
    dp.register_message_handler(read_fsm_cats, state=None)
    dp.register_message_handler(to_start, regexp='В начало', state='*')
