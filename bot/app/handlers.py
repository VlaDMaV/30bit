from datetime import datetime
from math import ceil

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import config
import app.keyboards as kb
import app.database.requests as rq


REVIEWS_PER_PAGE = 5

router = Router()

bot = Bot(token=config.bot_token.get_secret_value())

class Reg(StatesGroup):
    # Состояние для обратной связи
    name = State()  # Состояние для ввода имени
    number = State()  # Состояние для ввода номера телефона
    feedback = State()  # Состояние для обратной связи

class Review(StatesGroup):
    # Состояние для отзыва
    name = State()  # Состояние для ввода имени
    number = State()  # Состояние для ввода номера телефона
    rating = State() # Состояние для оценки
    review_text = State()  # Состояние для ввода текста отзыва
    edit_text = State()
    edit_rating = State()


# Хэндлер на команду /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    existing_user = await rq.get_user(user.id)

    if not existing_user:
        await rq.set_user(user.id, user.full_name, user.username)  # Сохраняем пользователя в БД, если его нет

    await message.answer("Добро пожаловать в бота компании 30БИТ!\n\n🛠️ Что умеет бот?", reply_markup=kb.main)


@router.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.edit_text("30бит — больше чем код. Мы — команда,"
                                     "которая превращает сложные задачи в элегантные IT-решения.\n\n"
                                     "Наш принцип: «30 бит точности — 100% результат».", reply_markup=kb.aboutus)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("Добро пожаловать в бота компании 30БИТ!\n\n🛠️ Что умеет бот?", reply_markup=kb.main)


@router.callback_query(F.data == "feedback")
async def feedback(callback: CallbackQuery, state: FSMContext):
    last_feedback = await rq.get_last_feedback_time(callback.from_user.id)
    
    if last_feedback and (datetime.now() - last_feedback).days < 1:
        await callback.message.edit_text(
            f"❌ Вы уже отправляли обратную связь сегодня.\n"
            f"Попробуйте снова через 24 часа.",
            reply_markup=kb.back_to_main
        )
        return

    user = await rq.get_user(callback.from_user.id)
    if user.name == callback.from_user.full_name:
        await callback.message.edit_text("Для обратной связи, пожалуйста, введите ваше имя:")
        await state.set_state(Reg.name)
    elif user.number:
        await state.update_data(name=user.name, number=user.number)
        await state.set_state(Reg.feedback)
        await callback.message.edit_text("Введите ваше сообщение:")
    else:
        await state.update_data(name=user.name)
        await state.set_state(Reg.number)
        await callback.message.edit_text("Введите ваш номер телефона:")


@router.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name or len(name) < 2 or not name.replace(" ", "").isalpha():
        await message.answer("Пожалуйста, введите корректное имя (минимум 2 буквы, только буквы).")
        return
    await state.update_data(name=name)

    user = await rq.get_user(message.from_user.id)

    if user.number:
        await state.update_data(number=user.number)
        await state.set_state(Reg.feedback)
        await message.answer("Введите ваше сообщение:")
    else:
        await state.set_state(Reg.number)
        await message.answer("Введите ваш номер телефона:")


@router.message(Reg.number)
async def reg_third(message: Message, state: FSMContext):
    cleaned_number = await rq.validate_russian_phone_number(message.text)
    if cleaned_number is None:
        await message.answer("Пожалуйста, введите корректный российский номер в формате +7XXXXXXXXXX.")
        return

    # Получаем name из FSM
    data = await state.get_data()
    name = data.get("name", "")

    await rq.set_user(
        tg_id=message.from_user.id,
        name=name,
        username=message.from_user.username,
        number=cleaned_number
    )
    
    await state.update_data(number=cleaned_number)
    await state.set_state(Reg.feedback)
    await message.answer("Введите ваше сообщение:")


@router.message(Reg.feedback)
async def reg_fourth(message: Message, state: FSMContext):
    feedback = message.text.strip()
    if not feedback or len(feedback) < 10:
        await message.answer("Пожалуйста, введите отзыв (минимум 10 символов).")
        return
    await state.update_data(feedback=feedback)
    data = await state.get_data()
    
    # Формируем текст для админа
    admin_text = (
        f"📩 Новое сообщение от пользователя\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['number']}\n"
        f"💬 Сообщение: {data['feedback']}"
    )

    # Отправляем админу
    try:
        await bot.send_message(chat_id=config.admin_id, text=admin_text)
        await rq.save_feedback(tg_id=message.from_user.id, message_text=data['feedback'])
        await message.answer(
            "✅ Ваше сообщение отправлено. Спасибо!",
            reply_markup=kb.back_to_main
        )
    except Exception as e:
        await message.answer("⚠️ Ошибка при отправке сообщения.", reply_markup=kb.back_to_main)

    await state.clear()  # Очищаем состояние после завершения регистрации, чтобы не засорять бота


@router.callback_query(F.data == "review")
async def review(callback: CallbackQuery, state: FSMContext):
    existing_review = await rq.get_user_review(callback.from_user.id)
    if existing_review:
        await callback.message.edit_text(
            "❌ Вы уже оставляли отзыв. Спасибо!",
            reply_markup=kb.review_management()
        )
        return
    
    user = await rq.get_user(callback.from_user.id)

    if user.name == callback.from_user.full_name:
        await callback.message.edit_text("Для отзыва, пожалуйста, введите ваше имя:")
        await state.set_state(Review.name)
    elif user.number:
        await state.update_data(name=user.name, number=user.number)
        await state.set_state(Review.review_text)
        await callback.message.edit_text("Введите ваш отзыв:")
    else:
        await state.update_data(name=user.name)
        await state.set_state(Review.number)
        await callback.message.edit_text("Введите ваш номер телефона:")


@router.message(Review.name)
async def review_second(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name or len(name) < 2 or not name.replace(" ", "").isalpha():
        await message.answer("Пожалуйста, введите корректное имя (минимум 2 буквы, только буквы).")
        return
    await state.update_data(name=name)
    user = await rq.get_user(message.from_user.id)
    if user.number:
        await state.update_data(number=user.number)
        await state.set_state(Review.review_text)
        await message.answer("Введите ваш отзыв:")
    else:
        await state.set_state(Review.number)
        await message.answer("Введите ваш номер телефона:")


@router.message(Review.number)
async def review_third(message: Message, state: FSMContext):
    cleaned_number = await rq.validate_russian_phone_number(message.text)
    if cleaned_number is None:
        await message.answer("Пожалуйста, введите корректный российский номер в формате +7XXXXXXXXXX.")
        return

    # Получаем name из FSM
    data = await state.get_data()
    name = data.get("name", "")

    await rq.set_user(
        tg_id=message.from_user.id,
        name=name,
        username=message.from_user.username,
        number=cleaned_number
    )

    await state.update_data(number=cleaned_number)
    await state.set_state(Review.review_text)
    await message.answer("Введите ваш отзыв:")


@router.message(Review.review_text)
async def review_fourth(message: Message, state: FSMContext):
    review_text = message.text.strip()
    if not review_text or len(review_text) < 10:
        await message.answer("Пожалуйста, введите отзыв (минимум 10 символов).")
        return

    await state.update_data(review_text=review_text)
    await state.set_state(Review.rating)  # Переводим в состояние оценки
    await message.answer("Пожалуйста, оцените нашу работу:", reply_markup=kb.stars_rating())


@router.callback_query(F.data.startswith("rate_"), Review.rating)
async def process_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])  # Получаем оценку (1-5)
    await state.update_data(rating=rating)
    data = await state.get_data()

    # Формируем текст для админа с оценкой
    admin_text = (
        f"⭐ Новый отзыв от пользователя\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['number']}\n"
        f"💬 Отзыв: {data['review_text']}\n"
        f"⭐ Оценка: {'⭐' * rating} ({rating}/5)"
    )

    try:
        await bot.send_message(chat_id=config.admin_id, text=admin_text)
        await rq.save_review(
            tg_id=callback.from_user.id, 
            review_text=data['review_text'],
            rating=rating 
        )
        await callback.message.edit_text(
            f"✅ Спасибо за ваш отзыв и оценку {'⭐' * rating}!",
            reply_markup=kb.back_to_main
        )
    except Exception as e:
        await callback.message.edit_text(
            "⚠️ Ошибка при отправке отзыва.",
            reply_markup=kb.back_to_main
        )

    await state.clear()


@router.callback_query(F.data == "edit_review")
async def edit_review(callback: CallbackQuery, state: FSMContext):
    # Получаем текущий отзыв пользователя
    existing_review = await rq.get_user_review(callback.from_user.id)
    
    if not existing_review:
        await callback.message.edit_text(
            "❌ Отзыв не найден",
            reply_markup=kb.back_to_main
        )
        return
    
    # Сохраняем ID отзыва для последующего обновления
    await state.update_data(review_id=existing_review.id)
    
    # Переходим к редактированию текста
    await callback.message.edit_text(
        f"Текущий отзыв: {existing_review.review_text}.\n"
        f"Рейтинг: {existing_review.rating}⭐\n\n"
        "Введите новый текст отзыва:",
        reply_markup=kb.back_to_main
    )
    await state.set_state(Review.edit_text)


@router.message(Review.edit_text)
async def process_edit_review_text(message: Message, state: FSMContext):
    new_text = message.text.strip()
    if not new_text or len(new_text) < 10:
        await message.answer("Пожалуйста, введите отзыв (минимум 10 символов).")
        return
    
    await state.update_data(new_text=new_text)
    
    # Отправляем клавиатуру с рейтингом
    await message.answer("Выберите новый рейтинг:", reply_markup=kb.stars_rating())
    await state.set_state(Review.edit_rating)


@router.callback_query(F.data.startswith("rate_"), Review.edit_rating)
async def process_edit_review_rating(callback: CallbackQuery, state: FSMContext):
    # Извлекаем рейтинг из callback_data
    new_rating = int(callback.data.split("_")[1])
    
    data = await state.get_data()
    review_id = data.get('review_id')
    new_text = data.get('new_text')
    
    if not review_id or not new_text:
        await callback.message.edit_text(
            "❌ Ошибка: не найдены данные для обновления отзыва",
            reply_markup=kb.back_to_main
        )
        await state.clear()
        return
    
    success = await rq.update_review(review_id, new_text, new_rating)
    
    if success:
        await callback.message.edit_text(
            f"✅ Отзыв успешно обновлен!\n\n"
            f"Текст: {new_text}\n"
            f"Рейтинг: {new_rating}⭐",
            reply_markup=kb.back_to_main
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось обновить отзыв",
            reply_markup=kb.back_to_main
        )
    
    await state.clear()


@router.callback_query(F.data == "reviews")
async def show_reviews(callback: CallbackQuery):
    try:
        total_reviews = await rq.get_reviews_count()
        total_pages = ceil(total_reviews / REVIEWS_PER_PAGE) if total_reviews > 0 else 1
        
        reviews = await rq.get_all_reviews(limit=REVIEWS_PER_PAGE)
        
        if not reviews:
            await callback.message.edit_text(
                "📝 Пока нет ни одного отзыва. Будьте первым!",
                reply_markup=kb.back_to_main
            )
            return
            
        await rq.display_reviews_page(callback.message, reviews, 0, total_pages)
        
    except Exception as e:
        await callback.message.answer(
            f"⚠️ Произошла ошибка: {str(e)}",
            reply_markup=kb.back_to_main
        )


@router.callback_query(F.data.startswith("reviews_"))
async def paginate_reviews(callback: CallbackQuery):
    try:
        page = int(callback.data.split("_")[1])
        offset = page * REVIEWS_PER_PAGE
        
        reviews = await rq.get_all_reviews(limit=REVIEWS_PER_PAGE, offset=offset)
        total_reviews = await rq.get_reviews_count()
        total_pages = ceil(total_reviews / REVIEWS_PER_PAGE)
        
        await rq.display_reviews_page(callback.message, reviews, page, total_pages)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)