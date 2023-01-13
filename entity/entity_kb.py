from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# buttons at start
btn_start = KeyboardButton('Старт')

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)

kb_start.add(btn_start)

# buttons at choose entity
but_acc_change = KeyboardButton('Изменения в балансе')
but_bills = KeyboardButton('Счета')
but_kategories = KeyboardButton('Категории')
# but_report = KeyboardButton('Отчет')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(but_acc_change)\
         .row(but_bills, but_kategories)

# buttons at work with entity
but_create = KeyboardButton('Создать')
but_change = KeyboardButton('Изменить')
but_delete = KeyboardButton('Удалить')
but_show = KeyboardButton('Посмотреть')
but_cancel = KeyboardButton('Отмена')

kb_action = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_action.row(but_create, but_change).row(but_delete, but_show).row(but_cancel)
