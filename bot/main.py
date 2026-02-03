import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from api import APIError, create_valentine, get_credential, list_valentines_by_recipient


class States(StatesGroup):
    sending_card = State()
    sending_text = State()
    sending_track = State()
    getting_id = State()
    getting_password = State()


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить")],
        [KeyboardButton(text="Получить")],
    ],
    resize_keyboard=True,
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Назад")]],
    resize_keyboard=True,
)


async def on_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Привет!", reply_markup=main_kb)


async def on_send_btn(message: Message, state: FSMContext) -> None:
    await state.set_state(States.sending_card)
    await state.set_data({})
    await message.answer("Пришли номер открытки.", reply_markup=back_kb)


async def on_sending_card(message: Message, state: FSMContext) -> None:
    try:
        card_number = int(message.text.strip())
    except ValueError:
        await message.answer("Нужно число. Пришли номер открытки.")
        return
    await state.update_data(recipient_id=card_number)
    await state.set_state(States.sending_text)
    await message.answer("Напиши текст послания.", reply_markup=back_kb)


async def on_sending_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=(message.text or "").strip())
    await state.set_state(States.sending_track)
    await message.answer("Пришли ссылку на любимый трек.", reply_markup=back_kb)


async def on_sending_track(message: Message, state: FSMContext) -> None:
    await state.update_data(track_link=(message.text or "").strip())
    data = await state.get_data()
    await state.clear()
    try:
        val = await create_valentine(
            text=data["text"],
            track_link=data["track_link"],
            recipient_id=data["recipient_id"],
        )
        await message.answer(
            f"Валентинка отправлена (id {val['id']}).",
            reply_markup=main_kb,
        )
    except APIError as e:
        await message.answer(
            f"Ошибка: {e.detail}",
            reply_markup=main_kb,
        )


async def on_get_btn(message: Message, state: FSMContext) -> None:
    await state.set_state(States.getting_id)
    await state.set_data({})
    await message.answer("Введи id.", reply_markup=back_kb)


async def on_getting_id(message: Message, state: FSMContext) -> None:
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("Нужно число. Введи id.")
        return
    await state.update_data(credential_id=user_id)
    await state.set_state(States.getting_password)
    await message.answer("Введи пароль.", reply_markup=back_kb)


async def on_getting_password(message: Message, state: FSMContext) -> None:
    password = (message.text or "").strip()
    data = await state.get_data()
    await state.clear()
    credential_id = data["credential_id"]
    try:
        cred = await get_credential(credential_id)
    except APIError as e:
        await message.answer(f"Ошибка: {e.detail}", reply_markup=main_kb)
        return
    if cred.get("password") != password:
        await message.answer("Неверный пароль.", reply_markup=main_kb)
        return
    try:
        valentines = await list_valentines_by_recipient(credential_id)
    except APIError as e:
        await message.answer(f"Ошибка: {e.detail}", reply_markup=main_kb)
        return
    if not valentines:
        await message.answer("У тебя нет валентинок.", reply_markup=main_kb)
        return
    for v in valentines:
        await message.answer(f"{v.get('text', '')}\n{v.get('track_link', '')}")
    await message.answer("Готово.", reply_markup=main_kb)


async def on_back(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Возврат в меню.", reply_markup=main_kb)


async def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("Задай переменную окружения BOT_TOKEN")
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.register(on_start, CommandStart())
    dp.message.register(on_back, F.text == "Назад")
    dp.message.register(on_send_btn, F.text == "Отправить")
    dp.message.register(on_get_btn, F.text == "Получить")
    dp.message.register(on_sending_card, StateFilter(States.sending_card), F.text)
    dp.message.register(on_sending_text, StateFilter(States.sending_text), F.text)
    dp.message.register(on_sending_track, StateFilter(States.sending_track), F.text)
    dp.message.register(on_getting_id, StateFilter(States.getting_id), F.text)
    dp.message.register(on_getting_password, StateFilter(States.getting_password), F.text)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
