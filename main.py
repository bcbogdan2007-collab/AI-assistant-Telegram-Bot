"""
Telegram-бот + Google Gemini API (демо-проект для портфолио).

Принципы работы:
  • каждое сообщение обрабатывается отдельно, история диалога не хранится;
  • база данных и файлы для хранения данных не используются;
  • тексты сообщений пользователей не логируются и не сохраняются.
"""
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

# ======================= Настройки =======================
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Модель можно поменять в .env, не трогая код (список моделей: ai.google.dev/gemini-api/docs/models)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

TELEGRAM_MESSAGE_LIMIT = 4096

SYSTEM_PROMPT = (
    "Ты — дружелюбный и полезный ИИ-ассистент в Telegram. "
    "Отвечай на том языке, на котором написал пользователь. "
    "Пиши понятно и по делу, структурируй ответ короткими абзацами. "
    "Не используй Markdown-разметку (звёздочки, решётки, обратные кавычки): "
    "для списков используй обычные дефисы или цифры."
)

WELCOME_TEXT = (
    "👋 <b>Добро пожаловать!</b>\n\n"
    "Этот бот демонстрирует интеграцию <b>Telegram</b> и искусственного интеллекта <b>Google Gemini</b>.\n\n"
    "С его помощью можно:\n\n"
    "✅ получать ответы на вопросы;\n"
    "✅ задать нужные параметры для ответов и стилистику общения под ваши нужды;\n"
    "✅ разбираться в сложных темах;\n"
    "✅ получать консультации и рекомендации;\n"
    "✅ генерировать идеи для проектов;\n"
    "✅ получать помощь в обучении;\n"
    "✅ генерировать тексты и планы.\n\n"
    "Бот обрабатывает запросы в режиме реального времени и генерирует ответы "
    "с использованием современных технологий искусственного интеллекта.\n\n"
    "<i>(для заказа такого бота для любых задач с полным обслуживанием напишите сюда: @dark_baga7)</i>\n\n"
    "✍️ <b>Просто отправьте любое сообщение и получите ответ.</b>"
)

# ======================= Логирование =======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("gemini_bot")
# Сторонние библиотеки не должны засорять консоль подробными логами
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)

# ======================= Проверка окружения =======================
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    logger.error(
        "Не заданы TELEGRAM_BOT_TOKEN и/или GEMINI_API_KEY. "
        "Скопируйте .env.example в .env и заполните значения."
    )
    sys.exit(1)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
router = Router()


# ======================= Работа с Gemini =======================
async def generate_response(prompt: str) -> str:
    """Отправляет один запрос в Gemini и возвращает текст ответа.

    Контекст диалога не передаётся и не сохраняется: каждый вызов независим.
    Ошибки API перехватываются и превращаются в понятное пользователю сообщение.
    """
    try:
        response = await gemini_client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            # Например, ответ заблокирован фильтрами безопасности
            return "🤔 Не удалось сформировать ответ на этот запрос. Попробуйте переформулировать вопрос."
        return text

    except genai_errors.APIError as e:
        code = getattr(e, "code", None)
        logger.error("Ошибка Gemini API (код %s)", code)  # текст запроса не логируем
        if code == 429:
            return "⏳ Слишком много запросов к ИИ. Подождите немного и попробуйте снова."
        if code in (401, 403):
            return "🔑 Проблема с доступом к Gemini API. Сообщите администратору бота."
        return "⚠️ Сервис ИИ временно недоступен. Попробуйте чуть позже."

    except Exception:
        logger.exception("Непредвиденная ошибка при обращении к Gemini")
        return "⚠️ Произошла непредвиденная ошибка. Попробуйте ещё раз."


def split_text(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    """Режет длинный ответ на части, допустимые в Telegram (до 4096 символов)."""
    chunks: list[str] = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks


# ======================= Обработчики =======================
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT)


@router.message(F.text)
async def handle_text(message: Message, bot: Bot) -> None:
    logger.info("Получен запрос от chat_id=%s", message.chat.id)  # без текста сообщения

    # Пока Gemini думает, показываем «печатает…»
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        answer = await generate_response(message.text)

    # Ответ ИИ отправляем без HTML-разметки, чтобы случайные символы < > & не ломали сообщение
    for chunk in split_text(answer):
        await message.answer(chunk, parse_mode=None)


@router.message()
async def handle_other(message: Message) -> None:
    await message.answer("📎 Я понимаю только текстовые сообщения. Напишите ваш вопрос текстом.")


# ======================= Запуск =======================
async def main() -> None:
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен (модель: %s)", GEMINI_MODEL)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Завершение работы")
