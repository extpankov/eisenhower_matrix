from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN

Bot = Bot(token=TOKEN)
dp = Dispatcher(bot=Bot, storage=MemoryStorage())