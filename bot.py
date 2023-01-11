from aiogram.utils import executor

from common_obj import dp
from processes.client import reg_processes_client 
from processes.Bill import reg_processes_bill_create,\
                           reg_processes_bill_read,\
                           reg_processes_bill_change,\
                           reg_processes_bill_delete

from processes.Category import reg_processes_cat_create,\
                               reg_processes_cats_read,\
                               reg_processes_cat_change,\
                               reg_processes_cat_delete

from processes.AccChange import reg_processes_acc_change_create,\
                                reg_processes_acc_change_read
from processes.Users.create_user import reg_processes_user
from handlers.client import reg_handlers_client


async def on_startup(_):
    print("Бот запущен")

if __name__ == '__main__':
    reg_handlers_client(dp)

    reg_processes_bill_create(dp)
    reg_processes_bill_read(dp)
    reg_processes_bill_change(dp)
    reg_processes_bill_delete(dp)

    reg_processes_cat_create(dp)
    reg_processes_cats_read(dp)
    reg_processes_cat_change(dp)
    reg_processes_cat_delete(dp)

    reg_processes_acc_change_create(dp)
    reg_processes_acc_change_read(dp)

    reg_processes_client(dp)
    reg_processes_user(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)