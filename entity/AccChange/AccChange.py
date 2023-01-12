from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger
from datetime import datetime

from database import Postgres
from processes import common_handlers


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
            cursor.execute(f""" SELECT acc_change.acc_change_id,
                                    acc_change.amount,
                                    acc_change.type,
                                    acc_change.record_date,
                                    category.cat_name,
                                    bill.bill_name
                                FROM acc_change AS acc

                                INNER JOIN category ON category.user_id = acc_change.user_id
                                                    AND category.cat_id = acc_change.cat_id

                                INNER JOIN bill ON bill.user_id = acc.user_id
                                                AND bill.bill_id = acc.bill_id

                                WHERE acc_change.user_id = {user_id}
                                    AND acc_change.acc_change_id = {acc_change_id};""")

            logger.info(f'{cursor.fetchall()[0]}')

            return cursor.fetchall()[0]

            


    # @staticmethod
    # async def choose_action(message: types.Message, state: FSMContext):

    #     if 'В начало' in message.text:
    #         await common_handlers.to_start(message, state)

    #     state.finish()
    
    #     if 'Посмотреть' in message.text:
    #         await exist_fsm_acc_change(message, 'read')

    #     elif 'Изменить' in message.text:
    #         await exist_fsm_acc_change(message, 'change')

    #     elif 'Удалить' in message.text:
    #         await exist_fsm_acc_change(message, 'delete')

    #     elif 'Создать' in message.text:
    #         await create_fsm_acc_change(message)