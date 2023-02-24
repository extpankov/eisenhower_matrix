from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from management.dispatcher import Bot, dp

@dp.message_handler(commands=['start'])
async def start_handler(message: Message):
    if not message is None:
        from_user_name = message.from_user.full_name
        from_user_id = message.from_user.id
    await start(from_user_name, from_user_id)
    # msg = f"Добро пожаловать, {from_user_name if from_user_name != '' else 'аноним'}!\n\n" +\
    # "Воспользуйтесь клавиатурой и выберите дальнейшее действие"
    # keyboard = InlineKeyboardMarkup(row_width=2)
    # keyboard.row(InlineKeyboardButton(text="📊 - Матрица Эйзенхауэра", callback_data="goto_matrix"))
    # keyboard.row(InlineKeyboardButton(text = "👨‍🔧 - Личный  кабинет", callback_data="goto_lk"), InlineKeyboardButton(text = "ℹ - О проекте", callback_data="goto_about"))
    # await Bot.send_message(chat_id=from_user_id, text=msg, parse_mode="HTML", reply_markup=keyboard)
    # await message.delete()

async def start(name, id):
    msg = f"Добро пожаловать, {name if name != '' else 'аноним'}!\n\n" +\
    "Воспользуйтесь клавиатурой и выберите дальнейшее действие"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(InlineKeyboardButton(text="📊 - Матрица Эйзенхауэра", callback_data="goto_matrix"))
    keyboard.row(InlineKeyboardButton(text = "👨‍🔧 - Личный  кабинет", callback_data="goto_lk"), InlineKeyboardButton(text = "ℹ - О проекте", callback_data="goto_about"))
    await Bot.send_message(chat_id=id, text=msg, parse_mode="HTML", reply_markup=keyboard)