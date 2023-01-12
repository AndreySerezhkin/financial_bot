from aiogram import types
from loguru import logger

from database import Postgres

class User():

    @staticmethod
    def get_user(user_id: types.base.Integer) -> list:
        """Получение пользователя"""

        with Postgres() as (con, cursor):
            query = f""" SELECT *
                        FROM users
                        WHERE user_id = {user_id} ;"""
            cursor.execute(query)

            return cursor.fetchall()[0]

    