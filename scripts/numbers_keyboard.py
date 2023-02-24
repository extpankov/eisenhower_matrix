from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CELLS_IN_ROW = 4 # from 1 to 5

async def get_numbers_keyboard(i):
    keyboard = InlineKeyboardMarkup(row_width=CELLS_IN_ROW)
    btns = list()
    number = 1
    if i > CELLS_IN_ROW:
        quantity_rows = i // CELLS_IN_ROW
        for j in range(quantity_rows + 1):
            if j != quantity_rows:
                for k in range(CELLS_IN_ROW):
                    btns.append(InlineKeyboardButton(str(number), callback_data=str(number)))
                    number += 1
                cellc_in_row(CELLS_IN_ROW, keyboard, btns)
                btns = list()
            else:
                f = i % CELLS_IN_ROW
                for k in range(f):
                    btns.append(InlineKeyboardButton(str(number), callback_data=str(number)))
                    number += 1
                cellc_in_row(f, keyboard, btns)
                btns = list()
    else:
        for k in range(i):
            btns.append(InlineKeyboardButton(str(number), callback_data=str(number)))
            number += 1
        cellc_in_row(i, keyboard, btns)
        btns = list()
    return keyboard
    

def cellc_in_row(CELLS_IN_ROW, keyboard, btns):
    if CELLS_IN_ROW == 1:
        return keyboard.row(btns[0])
    elif CELLS_IN_ROW == 2:
        return keyboard.row(btns[0], btns[1])
    elif CELLS_IN_ROW == 3:
        return keyboard.row(btns[0], btns[1], btns[2])
    elif CELLS_IN_ROW == 4:
        return keyboard.row(btns[0], btns[1], btns[2], btns[3])
    elif CELLS_IN_ROW == 5:
        return keyboard.row(btns[0], btns[1], btns[2], btns[3], btns[4])