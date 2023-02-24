from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from management.dispatcher import Bot, dp
from database.Database import Database
from .start_handler import start

db = Database()
TYPES = ['Важно и срочно', 'Важно и не срочно', 'Не важно и срочно', 'Не важно и не срочно']

class AddRecordState(StatesGroup):
    input_name = State()
    input_desc = State()
    input_date = State()

@dp.callback_query_handler(text="goto_matrix")
async def matrix(query: CallbackQuery):
    msg = "<b>=== МАТРИЦА ЭЙЗЕНХАУЭРА ===</b>\n\n"+\
    "Количество Ваших текущих задач:\n\n" +\
    f"<b>Важно и срочно</b>: {len(db.get_records(query.from_user.id, 0))}\n" +\
    f"<b>Важно и не срочно</b>: {len(db.get_records(query.from_user.id, 1))}\n" +\
    f"<b>Не важно и срочно</b>: {len(db.get_records(query.from_user.id, 2))}\n" +\
    f"<b>Не важно и не срочно</b>: {len(db.get_records(query.from_user.id, 3))}\n"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(InlineKeyboardButton(text="Подробнее", callback_data="matrix_more"), InlineKeyboardButton(text="Назад", callback_data="mainmenu"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query_handler(text="mainmenu")
async def mainmenu(query: CallbackQuery):
    await query.message.delete()
    await start(query.from_user.full_name, query.from_user.id)

@dp.callback_query_handler(text="matrix_more")
async def matrix_more(query: CallbackQuery, state: FSMContext):
    global TYPES
    async with state.proxy() as data:
        try:
            active_type = data["active_type"]
        except:
            active_type = 0
            data["active_type"] = active_type
    msg = await recs_to_msg(query.from_user.id, active_type)
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(InlineKeyboardButton(text="Управлять", callback_data="matrix_edit"), InlineKeyboardButton(text="Вернуться назад", callback_data="matrix_goto_mm"))
    keyboard.row(InlineKeyboardButton(text="<-- Назад", callback_data="matrix_return"), InlineKeyboardButton(text="Вперёд -->", callback_data="matrix_forward"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query_handler(text="matrix_return")
async def matrix_return(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        active_type = data["active_type"]
    if active_type == 0:
        await query.answer("Невозможно вернуться назад")
        return True
    async with state.proxy() as data:
        data["active_type"] = active_type - 1
    await matrix_more(query, state)

@dp.callback_query_handler(text="matrix_forward")
async def matrix_forward(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        active_type = data["active_type"]
    if active_type == 3:
        await query.answer("Невозможно перейти впёред")
        return True
    async with state.proxy() as data:
        data["active_type"] = active_type + 1
    await matrix_more(query, state)

@dp.callback_query_handler(text="matrix_goto_mm")
async def matrix_goto_mm(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["active_type"] = 0
    await matrix(query)

@dp.callback_query_handler(text="matrix_edit")
async def matrix_edit(query: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(InlineKeyboardButton(text="Добавить", callback_data="matrix_add_record"), InlineKeyboardButton(text="Закрыть", callback_data="123123113"))
    keyboard.row(InlineKeyboardButton(text="Изменить", callback_data="213123123"), InlineKeyboardButton(text="Делегировать", callback_data="123123113"))
    keyboard.row(InlineKeyboardButton(text="Отметить выполнение", callback_data="12312321"))
    keyboard.row(InlineKeyboardButton(text="<-- Назад", callback_data="matrix_return"), InlineKeyboardButton(text="Вперёд -->", callback_data="matrix_forward"))
    await query.message.edit_reply_markup(keyboard)

@dp.callback_query_handler(text="matrix_add_record")
async def matrix_add_record(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        active_type = data["active_type"]
        data["query"] = query
        data["query_message_text"] = query.message.text
        data["is_urgent"] = False if active_type == 0 or active_type == 2 else True
    msg = query.message.text +\
    "\n\n<i>Введите название задачи:</i>"
    await query.message.edit_text(text=msg, reply_markup=InlineKeyboardMarkup(), parse_mode="HTML")
    await AddRecordState.input_name.set()

@dp.message_handler(state=AddRecordState.input_name)
async def matrix_add_record_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["new_record"] = {
            "name": message.text
        }
        query = data["query"]
        query_message_text = data["query_message_text"]
    await message.delete()
    msg = query_message_text +\
    "\n\n<i>Введите описание задачи:</i>"
    await query.message.edit_text(text=msg, reply_markup=InlineKeyboardMarkup(), parse_mode="HTML")
    await AddRecordState.input_desc.set()

@dp.message_handler(state=AddRecordState.input_desc)
async def matrix_add_record_desc(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["new_record"].update(desc = message.text)
        query = data["query"]
        query_message_text = data["query_message_text"]
    await message.delete()
    msg = query_message_text +\
    "\n\n<i>Введите дату завершения задачи:</i>"
    await query.message.edit_text(text=msg, reply_markup=InlineKeyboardMarkup(), parse_mode="HTML")
    await AddRecordState.input_date.set()

@dp.message_handler(state=AddRecordState.input_date)
async def matrix_add_record_date(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["new_record"].update(deadline = message.text)
        query = data["query"]
        new_record = data["new_record"]
        active_type = data["active_type"]
    await message.delete()
    db.add_record(message.from_user.id, active_type, new_record["name"], new_record["desc"], new_record["deadline"])
    msg = "<b>Запись добавлена!</b>\n\n"+\
    f"Название: {new_record['name']}\n" +\
    f"Описание: {new_record['desc']}\n" +\
    f"Дата завершения: {new_record['deadline']}"
    await query.message.edit_text(text=msg, reply_markup=InlineKeyboardMarkup(), parse_mode="HTML")
    await AddRecordState.next()
async def recs_to_msg(id, active_type):
    records = db.get_records(id, active_type)
    msg = f"<b>- {TYPES[active_type]} -</b>\n\n"
    c = 1
    for r in records:
        msg = msg + f"{c}. {r[2]}\n"
        if active_type == 0 or active_type == 2:
            msg = msg + f"   <i>Срок выполнения до: <b>{r[4]}</b>\n</i>"
        c += 1
    return msg