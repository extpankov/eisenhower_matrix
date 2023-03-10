from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from management.dispatcher import Bot, dp
from database.Database import Database
from .start_handler import start
from scripts.numbers_keyboard import get_numbers_keyboard

db = Database()
TYPES = ['Важно и срочно', 'Важно и не срочно', 'Не важно и срочно', 'Не важно и не срочно']
kb_skip = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Пропустить', callback_data='skip'))

class AddRecordState(StatesGroup):
    input_name = State()
    input_desc = State()
    input_date = State()

class RemoveRecordState(StatesGroup):
    choosing = State()

class EditRecordState(StatesGroup):
    choosing = State()
    choosing_data = State()
    editing_data = State()

class DelegationRecordState(StatesGroup):
    choosing = State()
    choosing_new_type = State()

class CompletionRecordState(StatesGroup):
    choosing = State()

@dp.callback_query_handler(text="goto_matrix")
async def matrix(query: CallbackQuery):
    msg = "<b>=== МАТРИЦА ЭЙЗЕНХАУЭРА ===</b>\n\n"+\
    "Количество Ваших текущих задач:\n\n" +\
    f"<b>Важно и срочно</b>: {len(db.get_records(query.from_user.id, 0)) - len(db.get_completed_records(query.from_user.id, 0))}\n" +\
    f"<b>Важно и не срочно</b>: {len(db.get_records(query.from_user.id, 1)) - len(db.get_completed_records(query.from_user.id, 1))}\n" +\
    f"<b>Не важно и срочно</b>: {len(db.get_records(query.from_user.id, 2)) - len(db.get_completed_records(query.from_user.id, 2))}\n" +\
    f"<b>Не важно и не срочно</b>: {len(db.get_records(query.from_user.id, 3)) - len(db.get_completed_records(query.from_user.id, 3))}\n"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(InlineKeyboardButton(text="▶ Подробнее", callback_data="matrix_more"), InlineKeyboardButton(text="↩ Назад", callback_data="mainmenu"))
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
    keyboard.row(InlineKeyboardButton(text="👨‍🔧 Управлять", callback_data="matrix_edit"), InlineKeyboardButton(text="↩ Главное меню", callback_data="matrix_goto_mm"))
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
    keyboard.row(InlineKeyboardButton(text="🆕 - Добавить", callback_data="matrix_add_record"), InlineKeyboardButton(text="❌ - Закрыть", callback_data="matrix_remove_record"))
    keyboard.row(InlineKeyboardButton(text="👨‍🔧 - Изменить", callback_data="matrix_edit_record"), InlineKeyboardButton(text="🔛 - Делегировать", callback_data="matrix_delegation_record"))
    keyboard.row(InlineKeyboardButton(text="✅ - Отметить выполнение", callback_data="matrix_complete_record"))
    keyboard.row(InlineKeyboardButton(text="<-- Назад", callback_data="matrix_return"), InlineKeyboardButton(text="Вперёд -->", callback_data="matrix_forward"))
    await query.message.edit_reply_markup(keyboard)

@dp.callback_query_handler(text="matrix_add_record")
async def matrix_add_record(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["query"] = query
        data["query_message_text"] = query.message.text
    msg = query.message.text +\
    "\n\n<i>Введите название задачи:</i>"
    await query.message.edit_text(text=msg, parse_mode="HTML")
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
    await query.message.edit_text(text=msg, reply_markup=kb_skip, parse_mode="HTML")
    await AddRecordState.input_desc.set()

@dp.message_handler(state=AddRecordState.input_desc)
async def matrix_add_record_desc(message: Message = None, state: FSMContext = None, is_skipped: bool = False):
    async with state.proxy() as data:
        data["new_record"].update(desc = message.text if not is_skipped else None)
        query = data["query"]
        query_message_text = data["query_message_text"]
        active_type = data["active_type"]
        new_record = data["new_record"]
    if message != None:
        await message.delete()
    is_urgent = False if active_type == 1 or active_type == 3 else True
    if is_urgent:
        msg = query_message_text +\
        "\n\n<i>Введите дату завершения задачи:</i>"
        await query.message.edit_text(text=msg, reply_markup=kb_skip, parse_mode="HTML")
        await AddRecordState.input_date.set()
    else:
        db.add_record(message.from_user.id, active_type, new_record["name"], new_record["desc"])
        msg = "<b>Запись добавлена!</b>\n\n"+\
        f"Название: {new_record['name']}\n" +\
        f"Описание: {new_record['desc']}\n"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
        await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
        for i in range(2):
            await AddRecordState.next()


@dp.message_handler(state=AddRecordState.input_date)
async def matrix_add_record_date(message: Message = None, state: FSMContext = None, is_skipped: bool = False):
    async with state.proxy() as data:
        data["new_record"].update(deadline = message.text if not is_skipped else None)
        query = data["query"]
        new_record = data["new_record"]
        active_type = data["active_type"]
    if message != None:
        await message.delete()
    db.add_record(query.from_user.id, active_type, new_record["name"], new_record["desc"], new_record["deadline"])
    msg = "<b>Запись добавлена!</b>\n\n"+\
    f"Название: {new_record['name']}\n"
    if new_record['desc'] != None:
        msg += f"Описание: {new_record['desc']}\n"
    if new_record['deadline'] != None:
        msg += f"Дата завершения: {new_record['deadline']}\n"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
    await AddRecordState.next()

async def recs_to_msg(id, active_type, is_desc = None):
    records = db.get_records(id, active_type)
    msg = f"<b>- {TYPES[active_type]} -</b>\n\n"
    c = 1
    for r in records:
        if bool(int(r[6])) == True:
            msg = msg + f"<del>{c}. {r[3]}</del>\n"
            if active_type == 0 or active_type == 2:
                msg = msg + f"   <del><i>Срок выполнения до: <b>{r[5]}</b>\n</i></del>"
        else:
            msg = msg + f"{c}. {r[3]}\n"
            if active_type == 0 or active_type == 2:
                msg = msg + f"   <i>Срок выполнения до: <b>{r[5]}</b>\n</i>"
        if is_desc == True and r[4] != None:
            msg = msg + f"   <i>Описание: {r[4]}\n</i>"
        c += 1
    return msg

@dp.callback_query_handler(state=RemoveRecordState.choosing)
async def matrix_remove_record_choosing(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        active_type = data["active_type"]
        data["query"] = query
    db.remove_record(query.from_user.id, active_type, int(query.data) - 1)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
    await query.message.edit_text(text="<b>Запись удалена!</b>", reply_markup=keyboard, parse_mode="HTML")
    await RemoveRecordState.next()

@dp.callback_query_handler(state=EditRecordState.choosing)
async def matrix_edit_record_choosing(query: CallbackQuery, state: FSMContext):
    edit_record = [query.from_user.id, int(query.data) - 1] # user`s id and record`s quantity number
    async with state.proxy() as data:
        data["query"] = query
        data["edit_record"] = edit_record
        active_type = data["active_type"]
    is_urgent = False if active_type == 1 or active_type == 3 else True
    rec = db.get_records(query.from_user.id, active_type)[int(query.data)-1]
    start_msg = f"- {TYPES[active_type]} -\n" +\
    f"{query.data}. {rec[3]}\n"

    async with state.proxy() as data:
        data["start_msg"] = start_msg
        
    msg = start_msg
    if is_urgent:
        msg = msg + f"  <i>Срок выполнения до: {rec[5]}</i>"
    msg = msg + "\n\n<i>Выберите данные для изменения:</i>"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(InlineKeyboardButton(text="Название", callback_data="matrix_edit_name"), InlineKeyboardButton(text="Описание", callback_data="matrix_edit_desc"))
    if is_urgent:
        keyboard.add(InlineKeyboardButton(text="Дата завершения", callback_data="matrix_edit_deadline"))
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
    await EditRecordState.next()

# !!
@dp.callback_query_handler(text="matrix_goto_mm", state=EditRecordState.choosing_data)
async def matrix_edit_goto_mm(query: CallbackQuery, state: FSMContext):
    await matrix_goto_mm(query, state)
    await EditRecordState.last()
    await EditRecordState.next()

@dp.callback_query_handler(state=EditRecordState.choosing_data)
async def matrix_edit_record_choosing_data(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        edit_record = data["edit_record"]
        start_msg = data["start_msg"]
    msg = start_msg
    if query.data == "matrix_edit_name":
        edit_record.append("name")
        msg = msg + f"\n\n<i>Введите новое название задачи:</i>"
    elif query.data == "matrix_edit_desc":
        edit_record.append("desc")
        msg = msg + f"\n\n<i>Введите новое описание задачи:</i>"
    else:
        edit_record.append("deadline")
        msg = msg + f"\n\n<i>Введите новую дату завершения задачи:</i>"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
    async with state.proxy() as data:
        data["edit_record"] = edit_record
        data["query"] = query
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
    await EditRecordState.next()

@dp.message_handler(state=EditRecordState.editing_data)
async def matrix_edit_record_editing_data(message: Message, state: FSMContext):
    text = message.text
    async with state.proxy() as data:
        edit_record = data["edit_record"]
        query = data["query"]
        active_type = data["active_type"]
    await message.delete()
    if edit_record[2] == "name":
        db.edit_record(query.from_user.id, active_type, edit_record[1], name = text)
    elif edit_record[2] == "desc":
        db.edit_record(query.from_user.id, active_type, edit_record[1], desc = text)
    elif edit_record[2] == "deadline":
        db.edit_record(query.from_user.id, active_type, edit_record[1], deadline = text)
    
    msg = "<b>Запись изменена!</b>\n\n"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
    await EditRecordState.next()

@dp.callback_query_handler(state=DelegationRecordState.choosing)
async def matrix_delegation_record_choosing(query: CallbackQuery, state: FSMContext):
    number = int(query.data) - 1
    
    async with state.proxy() as data:
        text = data["query_message_text"]
        data["delegation_record"] = [data["active_type"], number]

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(InlineKeyboardButton(text=TYPES[0], callback_data="0"), InlineKeyboardButton(text=TYPES[1], callback_data="1"))
    keyboard.add(InlineKeyboardButton(text=TYPES[2], callback_data="2"), InlineKeyboardButton(text=TYPES[3], callback_data="3"))

    msg = text +\
    "\n\n<i>Выберите группу, в которую нужно делегировать выбранную задачу:</i>"

    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
    await DelegationRecordState.next()
    
@dp.callback_query_handler(state=DelegationRecordState.choosing_new_type)
async def matrix_delegation_record_choosing_new_type(query: CallbackQuery, state: FSMContext):
    new_active_type = int(query.data)

    async with state.proxy() as data:
        delegation_record = data["delegation_record"]

    db.delegate_record(query.from_user.id, delegation_record[0], delegation_record[1], new_active_type)

    msg = "<b>Запись делегирована!</b>\n\n"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
    await DelegationRecordState.next()

@dp.callback_query_handler(state=CompletionRecordState.choosing)
async def matrix_complete_record_choosing(query: CallbackQuery, state: FSMContext):
    number = int(query.data) - 1
    
    async with state.proxy() as data:
        active_type = data["active_type"]

    db.complete_record(query.from_user.id, active_type, number)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="matrix_goto_mm"))
    await query.message.edit_text("<b>Запись отмечена как выполненная!</b>", reply_markup=keyboard, parse_mode="HTML")
    await CompletionRecordState.next()

async def matrix_typed_form(query: CallbackQuery, state: FSMContext, type: int):
    # 0 - Закрыть
    # 1 - Изменить
    # 2 - Делегировать
    # 3 - Отметить выполнение
    types_text = ["закрыть", "изменить", "делегировать", "отметить как выполненную"]
    types_states = [RemoveRecordState, EditRecordState, DelegationRecordState, CompletionRecordState]
    async with state.proxy() as data:
            active_type = data["active_type"]
            data["query"] = query
            data["query_message_text"] = query.message.text
    msg = query.message.text +\
    f"\n\n<i>Выберите номер задачи, которую нужно {types_text[type]}:</i>"
    keyboard = await get_numbers_keyboard(len(db.get_records(query.from_user.id, active_type)))
    keyboard.add(InlineKeyboardButton(text="Вернуться назад", callback_data="12312313213"))
    await query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode="HTML")
    await types_states[type].choosing.set()

@dp.callback_query_handler(text="matrix_remove_record")
async def matrix_remove_record(query: CallbackQuery, state: FSMContext):
    await matrix_typed_form(query, state, 0)

@dp.callback_query_handler(text="matrix_edit_record")
async def matrix_edit_record(query: CallbackQuery, state: FSMContext):
    await matrix_typed_form(query, state, 1)

@dp.callback_query_handler(text="matrix_delegation_record")
async def matrix_delegation_record(query: CallbackQuery, state: FSMContext):
    await matrix_typed_form(query, state, 2)

@dp.callback_query_handler(text="matrix_complete_record")
async def matrix_complete_record(query: CallbackQuery, state: FSMContext):
    await matrix_typed_form(query, state, 3)

skip_states = [AddRecordState.input_desc, AddRecordState.input_date]
for ss in skip_states:
    @dp.callback_query_handler(text="skip", state=ss)
    async def matrix_skip(query: CallbackQuery, state: FSMContext):
        st = await state.get_state()
        if st == 'AddRecordState:input_desc':
            await matrix_add_record_desc(state = state, is_skipped=True)
        elif st == 'AddRecordState:input_date':
            await matrix_add_record_date(state = state, is_skipped=True)