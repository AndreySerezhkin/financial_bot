from aiogram.utils import executor

from common_modules.common_objects import dp
from entity import reg_processes_client 
import bill.processes as bill

import category.processes as category

import accChange.processes as acc_change
import users.processes as user
from financial_bot.start_process import reg_handlers_client


async def on_startup(_):
    print("Бот запущен")

if __name__ == '__main__':
    reg_handlers_client(dp)

    bill.reg_processes_bill_create(dp)
    bill.reg_processes_bill_read(dp)
    bill.reg_processes_bill_change(dp)
    bill.reg_processes_bill_delete(dp)

    category.reg_processes_cat_create(dp)
    category.reg_processes_cats_read(dp)
    category.reg_processes_cat_change(dp)
    category.reg_processes_cat_delete(dp)

    acc_change.reg_processes_acc_change_create(dp)
    acc_change.reg_processes_acc_change_read(dp)
    acc_change.reg_processes_acc_change_delete(dp)
    acc_change.reg_processes_acc_change_change(dp)
    acc_change.reg_processes_acc_change_exist(dp)

    reg_processes_client(dp)
    user.reg_processes_user(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)