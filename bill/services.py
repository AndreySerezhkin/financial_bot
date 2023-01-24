from aiogram import types
from aiogram import Bot
from loguru import logger

from common_modules.database import Postgres
from .processes import create_bill
from common_modules.common_kb import generate_entity_btn

class Bill():

    @staticmethod
    async def get_user_bills(user_id: types.base.Integer) -> list:
        """Получение всех счетов пользователя"""

        with Postgres() as (con, cursor):
            query = f""" SELECT *
                         FROM bill
                         WHERE user_id = {user_id} ;"""
            cursor.execute(query)

            
            result = cursor.fetchall()
            logger.info(f'Select from user bills: {result}')

        return result


    @staticmethod
    def check_exist_users_bill(user_bills: list, bill_name: str) -> bool:
        """Проверка существования счёта у пользователя"""

        for row in user_bills:
            if row['bill_name'] == bill_name:
                return True

    @staticmethod
    def get_next_new_bill_id(user_bills: list) -> int:
        """Получение id для нового счёта """
        bill_id = 0

        for row in user_bills:
            if bill_id < row['bill_id']:
                bill_id = row['bill_id']

        return bill_id + 1

    @staticmethod
    async def get_bill_info_by_name(bill_name: str, user_id: types.base.Integer) -> dict:
        with Postgres() as (conn, cursor):
            cursor.execute(f""" SELECT *
                                FROM bill
                                WHERE bill_name = '{bill_name}'
                                  AND user_id = {user_id};""")

            result = cursor.fetchall()[0]
            logger.info(f'select from user bill names: {result}')

        acc_balance = float(result['acc_balance'])
        logger.info(f'acc_balance: {acc_balance}')

        if result['is_not_calc']:
            is_calc_text = 'Не учитывается в общем балансе'
        else:
            is_calc_text = 'Учитывается в общем балансе'


        return {'bill_id': result['bill_id'],
                'bill_name': result['bill_name'],
                'acc_balance': acc_balance,
                'is_calc_text': is_calc_text,
                'is_not_calc': result['is_not_calc']}

    @staticmethod
    async def create_bill_from_oth_proc(bot: Bot, message: types.Message) -> None:
        """Переход к созданию счёта из других процессов"""

        await bot.send_message(message.from_user.id,
                               ' '.join('''Пока нет доступных счетов(. 
                                           Давайте создадим, 
                                           а потом делайте с ним что хотите'''.split()))
        await create_bill.create_fsm_bill(message)


    @staticmethod
    async def send_user_bills_names(bot: Bot, message: types.Message, state, text: str) -> None:
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

    @staticmethod
    def fill_data_by_param(data: dict, param: str, text: str) -> None:
        if param == 'Название':

            field = 'bill_name'
            field_value = text

        elif param == 'Баланс счёта':

            field = 'acc_balance'
            field_value = int(float(text) * 100)

        elif param == 'Учёт в общем балансе':
            field = 'is_calc_text'
            if text == 'Да':
                field_value = 'Учитывается в общем балансе'
            else:
                field_value = 'Не учитывается в общем балансе'
            data[field] = field_value

            field = 'is_not_calc'
            field_value = False if text == 'Да' else True

        data[field] = field_value

        return field, field_value
