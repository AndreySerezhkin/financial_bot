from aiogram import types
from aiogram import Bot
from aiogram.dispatcher import FSMContext
from loguru import logger

from database import Postgres
from processes.Bill import create_bill
from keyboards.common_kb import generate_entity_btn

class Bill():

    @staticmethod
    async def get_user_bills(user_id: types.base.Integer) -> list:
        """Получение всех счетов пользователя"""

        with Postgres() as (con, cursor):
            query = f""" SELECT *
                         FROM bill
                         WHERE user_id = {user_id} ;"""
            cursor.execute(query)

            logger.info(f'Select from user bills: {cursor.fetchall()}')

            return cursor.fetchall()


    @staticmethod
    def check_exist_users_bill(user_bills: list, bill_name: str):
        """Проверка существования счёта у пользователя"""

        for row in user_bills:
            if row['bill_name'] == bill_name:
                return True

    @staticmethod
    def get_next_new_bill_id(user_bills: list):
        """Получение id для нового счёта """
        bill_id = 0

        for row in user_bills:
            if bill_id < row['bill_id']:
                bill_id = row['bill_id']

        return bill_id

    @staticmethod
    async def get_bill(message: types.Message):
        with Postgres() as (conn, cursor):
            cursor.execute(f""" SELECT *
                                FROM bill
                                WHERE bill_name = '{message.text}'
                                  AND user_id = {message.from_user.id};""")

            result = cursor.fetchall()[0]
            logger.info(f'select from user bill names: {result}')

        acc_balance = float(result['acc_balance'] / 100)
        logger.info(f'acc_balance: {acc_balance}')

        if result['is_not_calc']:
            is_calc = 'Не учитывается в общем балансе'
        else:
            is_calc = 'Учитывается в общем балансе'


        return {'bill_id': result['bill_id'],
                'bill_name': result['bill_name'],
                'acc_balance': acc_balance,
                'is_calc': is_calc}

    @staticmethod
    async def create_bill_from_oth_proc(bot: Bot, message: types.Message):
        """Переход к созданию счёта из других процессов"""

        await bot.send_message(message.from_user.id,
                               ' '.join('''Пока нет доступных счетов(. 
                                           Давайте создадим, 
                                           а потом делайте с ним что хотите'''.split()))
        await create_bill.create_fsm_bill(message)


    @staticmethod
    async def send_user_bills_names(bot: Bot, message: types.Message, state, text: str):
        """Отправка списка названий счетов"""

        result = await Bill.get_user_bills(user_id=message.from_user.id)

        bills = [x['bill_name'] for x in result]

        if len(bills) > 0:
            kb_read_bill = generate_entity_btn(bills, 3)

            await state.set()
            await bot.send_message(message.from_user.id,
                                   text,
                                   reply_markup=kb_read_bill)
        else:
            await Bill.create_bill_from_oth_proc(bot, message)
