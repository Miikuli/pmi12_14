import asyncio
from asyncio import Lock
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardRemove
from dotenv import load_dotenv
import os

lock = Lock()

load_dotenv()
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(os.getenv('TOKEN'))
# Диспетчер
dp = Dispatcher()

#class DB:
schedule = {}


class AddEventStates(StatesGroup):
    getting_date = State()
    getting_time = State()
    getting_text = State()

class GetScheduleStates(StatesGroup):
    getting_date = State()

# Хэндлер на команду /start
@dp.message(StateFilter(None), Command("start"))
async def start(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, text = "Привет, это я, твой персональный ежедневник! :) Чтобы добавить событие введите /add_event")

@dp.message(Command("add_event"))
async def add_event(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, text = "Введите дату события в формате ГГГГ-ММ-ДД: ")
    await state.set_state(AddEventStates.getting_date)

@dp.message(AddEventStates.getting_date)
async def process_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Введите время события в формате ЧЧ-ММ: ")
    await state.set_state(AddEventStates.getting_time)

@dp.message(AddEventStates.getting_time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("Введите описание события:")
    await state.set_state(AddEventStates.getting_text)

@dp.message(AddEventStates.getting_text)
async def process_text(message: Message, state: FSMContext):
    data = await state.get_data()
    date = data.get('date')
    time = data.get('time')
    text = message.text
    schedule[date] = {'time': time, 'text': text}
    await message.answer(f"Событие {text} на {date} в {time} добавлено в ежедневник! Для просмотра расписания напишите /get_schedule")
    await state.clear()

@dp.message(Command("get_schedule"))
async def get_schedule(message: Message, state: FSMContext):
    await message.answer("Введите дату для просмотра расписания в формате ГГГГ-ММ-ДД:")
    await state.set_state(GetScheduleStates.getting_date)

@dp.message(GetScheduleStates.getting_date)
async def process_get_schedule(message: Message, state: FSMContext):
    date = message.text
    events = schedule[date]
    answers = ''
    answers += f'{events["time"]}'
    answers += ' '
    answers += f'{events["text"]}\n'
    await message.answer(answers)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
