import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatAction

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token, message_handler):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.message_handler = message_handler
        self._register_handlers()
    
    def _register_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message()(self.handle_text_message)
    
    async def cmd_start(self, message: Message):
        logger.info(f"Command /start from user {message.from_user.id}")
        await message.answer("Привет! Я AI ассистент. Задай мне любой вопрос!")
    
    async def handle_text_message(self, message: Message):
        try:
            # Показываем индикатор "печатает..."
            await self.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING
            )
            
            # Обрабатываем сообщение через MessageHandler
            response = await self.message_handler.handle_message(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                text=message.text
            )
            
            # Отправляем ответ
            await message.answer(response)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await message.answer("Извините, произошла ошибка. Попробуйте еще раз.")
    
    async def start(self):
        logger.info("Bot started successfully")
        await self.dp.start_polling(self.bot)

