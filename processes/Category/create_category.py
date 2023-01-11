from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import db, Postgres
from common_obj import bot
from processes import common_handlers
from keyboards import common_kb
from entity.Category.Category import Category


class FSMCreationCat(StatesGroup):
    cat_name = State()


async def create_fsm_cat(message: types.Message):
    await FSMCreationCat.cat_name.set()
    await bot.send_message(message.from_user.id,
                           'Название категории',
                           reply_markup=common_kb.kb_cancel)


async def cancel_create(message: types.Message, state: FSMContext):
    await common_handlers.cancel_process(message, state)


async def write_name(message: types.Message, state: FSMContext):
    result = await Category.write_name(message)

    if result['cancel']:
        await bot.send_message(message.from_user.id,
                               'Категория с таким именем уже существует')
        await state.finish()
        await create_fsm_cat(message)
    else:
        with Postgres() as (conn, cursor):
            db.insert('category', {'cat_name': message.text,
                                   'cat_id': result['cat_id'] + 1,
                                   'user_id': message.from_user.id},
                    cursor=cursor, conn=conn)

        await bot.send_message(message.from_user.id,
                               f"Готово! Категория '{message.text}' создана")

        await common_handlers.to_start(message=message, state=state)


def reg_processes_cat_create(dp: Dispatcher):
    dp.register_message_handler(create_fsm_cat, state=None)
    dp.register_message_handler(cancel_create, regexp='Отмена', state='*')
    dp.register_message_handler(write_name, state=FSMCreationCat.cat_name)
