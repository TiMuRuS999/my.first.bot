import asyncio
import json
import logging
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Загрузка фактов из отдельного JSON-файла ---
with open("pets_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

CAT_BREEDS = data["cat_breeds"]
DOG_BREEDS = data["dog_breeds"]


# --- Машина состояний (FSM) для теста ---
class PetTest(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()


# --- Главное меню с инлайн-кнопками ---
def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🐾 Факты о кошках", callback_data="cat_facts")],
            [InlineKeyboardButton(text="🐶 Факты о собаках", callback_data="dog_facts")],
            [InlineKeyboardButton(text="📋 Тест на питомца", callback_data="start_test")],
            [InlineKeyboardButton(text="ℹ️️ Кто я", callback_data="who_am_i")],
        ]
    )


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот-путеводитель по миру питомцев. Выбери интересующую тебя кнопку:",
        reply_markup=get_main_keyboard(),
    )


# --- 1. Кнопка «Факты о кошках» ---
@dp.callback_query(F.data == "cat_facts")
async def process_cat_facts(callback: types.CallbackQuery):
    breed = random.choice(list(CAT_BREEDS.keys()))
    facts = CAT_BREEDS[breed]

    text = f"<b>Порода кошки: {breed}</b>\n\n"
    for i, fact in enumerate(facts, 1):
        text += f"{i}. {fact}\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# --- 2. Кнопка «Факты о собаках» ---
@dp.callback_query(F.data == "dog_facts")
async def process_dog_facts(callback: types.CallbackQuery):
    breed = random.choice(list(DOG_BREEDS.keys()))
    facts = DOG_BREEDS[breed]

    text = f"<b>Порода собаки: {breed}</b>\n\n"
    for i, fact in enumerate(facts, 1):
        text += f"{i}. {fact}\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# --- 4. Кнопка «Кто я» ---
@dp.callback_query(F.data == "who_am_i")
async def process_who_am_i(callback: types.CallbackQuery):
    text = (
        "ℹ️ <b>Кто я?</b>\n\n"
        "Я бот, который расскажет о различных питомцах. "
        "Я создан на языке Python с использованием библиотеки aiogram!"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# --- 3. Тест на питомца (FSM) ---
@dp.callback_query(F.data == "start_test")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(PetTest.q1)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Активный отдых на природе", callback_data="score_dog")],
            [InlineKeyboardButton(text="Уютный вечер дома с книгой", callback_data="score_cat")],
            [InlineKeyboardButton(text="И то, и другое по настроению", callback_data="score_balanced")],
        ]
    )
    await callback.message.answer(
        "Вопрос 1 из 5: Как ты предпочитаешь проводить свободное время?",
        reply_markup=keyboard,
    )
    await callback.answer()


@dp.callback_query(PetTest.q1, F.data.startswith("score_"))
async def process_q1(callback: types.CallbackQuery, state: FSMContext):
    score = 1 if callback.data == "score_dog" else (-1 if callback.data == "score_cat" else 0)
    await state.update_data(score=score)
    await state.set_state(PetTest.q2)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Просторный частный дом", callback_data="score_dog")],
            [InlineKeyboardButton(text="Уютная квартира", callback_data="score_cat")],
            [InlineKeyboardButton(text="Не имеет значения", callback_data="score_balanced")],
        ]
    )
    await callback.message.answer(
        "Вопрос 2 из 5: Какое у тебя жилье?", reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(PetTest.q2, F.data.startswith("score_"))
async def process_q2(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0) + (1 if callback.data == "score_dog" else (-1 if callback.data == "score_cat" else 0))
    await state.update_data(score=score)
    await state.set_state(PetTest.q3)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Люблю долгие активные прогулки", callback_data="score_dog")],
            [InlineKeyboardButton(text="Предпочитаю отдыхать дома", callback_data="score_cat")],
            [InlineKeyboardButton(text="Гуляю умеренно", callback_data="score_balanced")],
        ]
    )
    await callback.message.answer(
        "Вопрос 3 из 5: Как часто ты готов гулять на улице?", reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(PetTest.q3, F.data.startswith("score_"))
async def process_q3(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0) + (1 if callback.data == "score_dog" else (-1 if callback.data == "score_cat" else 0))
    await state.update_data(score=score)
    await state.set_state(PetTest.q4)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Преданный друг и компаньон", callback_data="score_dog")],
            [InlineKeyboardButton(text="Независимый и гордый питомец", callback_data="score_cat")],
            [InlineKeyboardButton(text="Ласковый мурлыка", callback_data="score_balanced")],
        ]
    )
    await callback.message.answer(
        "Вопрос 4 из 5: Какой характер питомца тебе ближе?", reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(PetTest.q4, F.data.startswith("score_"))
async def process_q4(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0) + (1 if callback.data == "score_dog" else (-1 if callback.data == "score_cat" else 0))
    await state.update_data(score=score)
    await state.set_state(PetTest.q5)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Готов уделять много времени дрессировке", callback_data="score_dog")],
            [InlineKeyboardButton(text="Хочу чтобы питомец был самостоятельным", callback_data="score_cat")],
            [InlineKeyboardButton(text="Предпочитаю золотую середину", callback_data="score_balanced")],
        ]
    )
    await callback.message.answer(
        "Вопрос 5 из 5: Сколько времени ты готов уделять уходу и воспитанию?",
        reply_markup=keyboard,
    )
    await callback.answer()


@dp.callback_query(PetTest.q5, F.data.startswith("score_"))
async def process_q5(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    final_score = data.get("score", 0) + (1 if callback.data == "score_dog" else (-1 if callback.data == "score_cat" else 0))

    if final_score > 0:
        result_pet = random.choice(["Лабрадор", "Корги", "Хаски"])
        pet_type = "собака"
    elif final_score < 0:
        result_pet = random.choice(["Мейн-кун", "Сфинкс", "Рэгдолл"])
        pet_type = "кошка"
    else:
        result_pet = random.choice(["Британская короткошерстная", "Пудель"])
        pet_type = "питомец"

    await callback.message.answer(
        f"🎉 <b>Тест завершен!</b>\n\n"
        f"Судя по твоим ответам, тебе идеально подойдет <b>{pet_type}</b> породы: <b>{result_pet}</b>! 🐾",
        parse_mode="HTML",
    )
    await state.clear()
    await callback.answer()


# Главная функция запуска бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())