from aiogram import types
from loguru import logger
from datetime import datetime
from aiogram.dispatcher import FSMContext

from common_modules.database import Postgres
from common_modules.common_handlers import to_start
from bill.services import Bill
from category.services import Category


class AccChange():

    @staticmethod
    def get_user_acc_changes(user_id: types.base.Integer, 
                            acc_change_type: str, 
                            record_date: datetime) -> dict:
        """Получение изменений счёта пользователя по дате и типу изменения"""

        with Postgres() as (conn, cursor):
            cursor.execute(f""" SELECT acc_change.acc_change_id,
                                    acc_change.amount,
                                    category.cat_name
                                FROM acc_change
                                INNER JOIN category ON category.user_id = acc_change.user_id
                                                    AND category.cat_id = acc_change.cat_id
                                WHERE acc_change.user_id = {user_id}
                                    AND acc_change.type = '{acc_change_type}'
                                    AND acc_change.record_date = '{record_date.strftime("%Y-%m-%d")}';""")
            
            acc_changes =  cursor.fetchall()

        acc_changes_dict = {}
        for row in acc_changes:
            logger.info(f'{row}')
            acc_changes_dict[f'acc{row["acc_change_id"]}'] = f"""{(row['amount'] / 100):.2f}\n'{row['cat_name']}'"""

        return acc_changes_dict


    @staticmethod
    def get_acc_change_info(user_id: types.base.Integer, acc_change_id) -> list[tuple]:
        with Postgres() as (conn, cursor):
            cursor.execute(f""" SELECT acc.acc_change_id,
                                    acc.amount,
                                    acc.type,
                                    acc.record_date,
                                    category.cat_name,
                                    bill.bill_name
                                FROM acc_change AS acc

                                INNER JOIN category ON category.user_id = acc.user_id
                                                    AND category.cat_id = acc.cat_id

                                INNER JOIN bill ON bill.user_id = acc.user_id
                                                AND bill.bill_id = acc.bill_id

                                WHERE acc.user_id = {user_id}
                                    AND acc.acc_change_id = {acc_change_id};""")
            
            result = cursor.fetchall()[0]

            logger.info(f'{result}, {type(result)}')

            return result

            
    @staticmethod
    async def fill_data_by_param(data: dict, param: str, text: str, user_id: types.base.Integer) -> None:
        """Заполнение выбранного параметра указанным значением"""

        if param == 'Счёт':

            field = 'bill_id'
            field_value = (await Bill.get_bill_info_by_name(bill_name=text, 
                                                            user_id=user_id))['bill_id']

        elif param == 'Сумма':

            field = 'amount'
            field_value = int(float(text) * 100)

        elif param == 'Тип':

            field = 'type'
            field_value = 'e' if text == 'Расход' else 'i'

        elif param == 'Дата':

            field = 'record_date'
            field_value = data['date']

        elif param == 'Категория':

            field = 'cat_id'
            field_value = await Category.get_cat_id_by_name(cat_name=text, 
                                                            user_id=user_id)

            

        data[field] = field_value

        return field, field_value
    

    async def choose_acc_change_action(message: types.Message, state: FSMContext):

        from .processes import existing_acc_change

        if 'Расход' in message.text or 'Доход' in message.text:

            await existing_acc_change.set_type_acc_change(message, state)

        elif message.text == 'В начало':
            await to_start(message, state)

        else:
            await existing_acc_change.exist_fsm_acc_change(message, action = 'change')