from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_cancel = KeyboardButton('Отмена')

# buttons when changing the balance
btn_expense = KeyboardButton('Расход')
btn_income = KeyboardButton('Доход')

kb_acc_change = ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True)

kb_acc_change.add(btn_expense, btn_income).row(btn_cancel)

# buttons when changing the balance
btn_today = KeyboardButton('Сегодня')
btn_yesterday = KeyboardButton('Вчера')
btn_oth_date = KeyboardButton('Другая дата')

kb_date = ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True)

kb_date.row(btn_today, btn_yesterday).add(btn_oth_date)

# buttons at end of create changing the balance
but_return = KeyboardButton('В начало')

kb_end_acc_change = ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)

kb_end_acc_change.add(btn_expense, btn_income).row(btn_oth_date).row(but_return)


# buttons when changing the balance
btn_cat = KeyboardButton('Категория')
btn_bill = KeyboardButton('Счёт')
btn_date = KeyboardButton('Дата')
btn_type = KeyboardButton('Тип')
btn_summ = KeyboardButton('Сумма')

kb_choose_param = ReplyKeyboardMarkup(resize_keyboard=True,
                                      one_time_keyboard=True)

kb_date.add(btn_cat, btn_bill, btn_date, btn_type, btn_summ)


but_create = KeyboardButton('Создать')
but_change = KeyboardButton('Изменить')
but_delete = KeyboardButton('Удалить')
but_show = KeyboardButton('Посмотреть')
but_cancel = KeyboardButton('В начало')

kb_choose_act = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_choose_act.row(but_create, but_change).row(but_delete, but_show).row(but_cancel)


def generate_action_kb(type) -> ReplyKeyboardMarkup:

    if type == 'e':
        btn_expense = KeyboardButton('Другой Расход')
        btn_income = KeyboardButton('Доход')
    else:
        btn_expense = KeyboardButton('Расход')
        btn_income = KeyboardButton('Другой Доход')

    btn_oth_date = KeyboardButton('Другая дата')
    

    kb_choose_action = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_choose_action.add(btn_expense, btn_income, btn_oth_date, KeyboardButton('В начало'))

    return kb_choose_action



