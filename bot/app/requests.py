from app.database.models import Feedback, Review, async_session
from app.database.models import User
from sqlalchemy import func, select, update

import app.keyboards as kb
from aiogram.types import Message
import re


async def set_user(tg_id, name=None, username=None, number=None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(
                tg_id=tg_id, 
                name=name, 
                username=username, 
                number=number
            ))
            await session.commit()

        if user and (user.name != name or user.username != username):
            user.name = name
            user.username = username
            await session.commit()

        if number:
            user.number = number
            await session.commit()


async def get_user(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def validate_russian_phone_number(raw_number: str) -> str | None:
    """
    Валидирует и нормализует российский номер телефона.

    Принимает номер в произвольном формате, возвращает номер в формате +7XXXXXXXXXX,
    
    либо None, если номер невалидный.
    """
    cleaned_number = re.sub(r"[^\d+]", "", raw_number.strip())

    if cleaned_number.startswith("8"):
        cleaned_number = "+7" + cleaned_number[1:]
    elif cleaned_number.startswith("7"):
        cleaned_number = "+7" + cleaned_number[1:]
    elif not cleaned_number.startswith("+7"):
        return None

    if not re.fullmatch(r"\+7\d{10}", cleaned_number):
        return None

    return cleaned_number


async def save_feedback(tg_id: int, message_text: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if user:
            feedback = Feedback(user_id=user.id, message_text=message_text)
            session.add(feedback)
            await session.commit()


async def get_last_feedback_time(tg_id: int):
    async with async_session() as session:
        user_result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return None

        feedback_result = await session.execute(
            select(Feedback.created_at)
            .where(Feedback.user_id == user.id)
            .order_by(Feedback.created_at.desc())
            .limit(1)
        )
        return feedback_result.scalar_one_or_none()


async def save_review(tg_id: int, review_text: str, rating: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if user:
            review = Review(user_id=user.id, review_text=review_text, rating=rating)
            session.add(review)
            await session.commit()


async def get_user_review(tg_id: int):
    async with async_session() as session:
        user_result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return None
        
        review_result = await session.execute(
            select(Review).where(Review.user_id == user.id)
        )
        return review_result.scalar_one_or_none()
    

async def update_review(review_id: int, new_text: str, new_rating: int = None) -> bool:
    async with async_session() as session:
        try:
            # Формируем словарь с обновляемыми полями
            update_data = {"review_text": new_text}
            if new_rating is not None:
                update_data["rating"] = new_rating
            
            await session.execute(
                update(Review)
                .where(Review.id == review_id)
                .values(**update_data)
            )
            await session.commit()
            return True
        except Exception as e:
            return False
        

async def get_all_reviews(limit: int = 5, offset: int = 0):
    async with async_session() as session:
        stmt = (
            select(Review)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        reviews = result.scalars().all()

        reviews_list = []
        for review in reviews:
            user = await session.get(User, review.user_id)
            user_name = getattr(user, "username", f"User#{review.user_id}")
            
            reviews_list.append({
                "id": review.id,
                "user_name": user_name,
                "text": review.review_text, 
                "rating": review.rating,
                "created_at": review.created_at.strftime("%d.%m.%Y %H:%M"),
            })
        return reviews_list
    

async def get_reviews_count():
    async with async_session() as session:
        result = await session.execute(select(func.count(Review.id)))
        return result.scalar()
    

async def display_reviews_page(message: Message, reviews: list, current_page: int, total_pages: int):
    text = "📝 Все отзывы:\n\n"
    
    for review in reviews:
        stars = "⭐" * review["rating"] if review["rating"] else "без оценки"
        text += (
            f"👤 {review['user_name']}\n"
            f"⭐ {stars}\n"
            f"📅 {review['created_at']}\n"
            f"💬 {review['text']}\n\n"
            f"{'-'*30}\n\n"
        )
    
    text += f"Страница {current_page + 1} из {total_pages}"
    
    await message.edit_text(
        text,
        reply_markup=kb.reviews_keyboard(page=current_page, total_pages=total_pages)
    )