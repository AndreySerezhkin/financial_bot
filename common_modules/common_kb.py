from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

but_yes = KeyboardButton('Да')
but_no = KeyboardButton('Нет')

kb_close_question = ReplyKeyboardMarkup(resize_keyboard=True,
                                        one_time_keyboard=True)

kb_close_question.row(but_yes, but_no)

# Cancel
but_cancel = KeyboardButton('Отмена')

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_cancel.add(but_cancel)

# To start
but_to_start = KeyboardButton('В начало')

kb_to_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_to_start.add(but_to_start)



# buttons when choosing to view entitys
def generate_entity_btn(list, size_line=1) -> ReplyKeyboardMarkup:

    kb_entity = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_entity.row(KeyboardButton('Отмена'))

    list = [KeyboardButton(x) for x in list]

    while len(list) != 0:
        pice = list[:size_line]
        for i in pice:
            button = i
            kb_entity.row(button)
        list = list[size_line:]

    return kb_entity

def generate_entity_btn_inline(dictionary: dict, size_line=1) -> ReplyKeyboardMarkup:

    kb_entity = InlineKeyboardMarkup(resize_keyboard=True)

    kb_list = [InlineKeyboardButton(text=text, callback_data=data) for data, text in dictionary.items()]

    while len(kb_list) != 0:
        pice = kb_list[:size_line]
        for i in pice:
            button = i
            kb_entity.row(button)
        kb_list = kb_list[size_line:]

    return kb_entity
