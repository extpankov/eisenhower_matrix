from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from management.dispatcher import dp
from config import VERSION

@dp.callback_query_handler(text="goto_about")
async def goto_about(query: CallbackQuery):
    msg = "<b>ℹ - О проекте</b>\n\n" +\
    "Матрица Эйзенхауэра (англ. Eisenhower Matrix) — метод тайм-менеджмента, помогающий вычленить из всего потока дел самые важные и срочные, и распределить остальные задачи по параметрам скорости их реализации и ценности, это способствует регулирования рабочей нагрузки.\n\n" +\
    f"Текущая версия приложения: {VERSION}\n\n" +\
    "© Roman Pankov, 2023"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton(text="GitHub автора", url="https://github.com/extpankov"))
    keyboard.add(InlineKeyboardButton(text="Подробнее о Матрице", url="https://ru.wikipedia.org/wiki/Матрица_Эйзенхауэр"))
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="mainmenu"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")