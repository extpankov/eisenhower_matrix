from aiogram import executor

from .dispatcher import dp

import handlers

executor.start_polling(dp, skip_updates=True)