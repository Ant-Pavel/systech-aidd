"""Unit-тесты для модуля conversation."""

from src.conversation import Conversation


class TestConversation:
    """Тесты для класса Conversation."""

    def test_add_message_single(self) -> None:
        """Тест добавления одного сообщения."""
        conversation = Conversation(max_history_messages=10)
        user_id, chat_id = 123, 456

        conversation.add_message(user_id, chat_id, "user", "Hello")

        history = conversation.get_history(user_id, chat_id)
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"

    def test_add_message_multiple(self) -> None:
        """Тест добавления нескольких сообщений."""
        conversation = Conversation(max_history_messages=10)
        user_id, chat_id = 123, 456

        conversation.add_message(user_id, chat_id, "user", "Hello")
        conversation.add_message(user_id, chat_id, "assistant", "Hi there!")
        conversation.add_message(user_id, chat_id, "user", "How are you?")

        history = conversation.get_history(user_id, chat_id)
        assert len(history) == 3
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"
        assert history[2]["role"] == "user"
        assert history[2]["content"] == "How are you?"

    def test_get_history_empty(self) -> None:
        """Тест получения пустой истории."""
        conversation = Conversation(max_history_messages=10)
        user_id, chat_id = 123, 456

        history = conversation.get_history(user_id, chat_id)

        assert history == []

    def test_get_history_with_messages(self) -> None:
        """Тест получения истории с сообщениями."""
        conversation = Conversation(max_history_messages=10)
        user_id, chat_id = 123, 456

        conversation.add_message(user_id, chat_id, "user", "Message 1")
        conversation.add_message(user_id, chat_id, "assistant", "Response 1")

        history = conversation.get_history(user_id, chat_id)

        assert len(history) == 2

    def test_clear_history_existing(self) -> None:
        """Тест очистки существующей истории."""
        conversation = Conversation(max_history_messages=10)
        user_id, chat_id = 123, 456

        conversation.add_message(user_id, chat_id, "user", "Hello")
        conversation.add_message(user_id, chat_id, "assistant", "Hi")

        assert len(conversation.get_history(user_id, chat_id)) == 2

        conversation.clear_history(user_id, chat_id)

        history = conversation.get_history(user_id, chat_id)
        assert history == []

    def test_clear_history_non_existing(self) -> None:
        """Тест очистки несуществующей истории (не должно быть ошибки)."""
        conversation = Conversation(max_history_messages=10)
        user_id, chat_id = 123, 456

        # Не должно быть ошибки
        conversation.clear_history(user_id, chat_id)

        history = conversation.get_history(user_id, chat_id)
        assert history == []

    def test_max_history_limit(self) -> None:
        """Тест ограничения количества сообщений в истории."""
        max_messages = 5
        conversation = Conversation(max_history_messages=max_messages)
        user_id, chat_id = 123, 456

        # Добавляем 10 сообщений
        for i in range(10):
            role = "user" if i % 2 == 0 else "assistant"
            conversation.add_message(user_id, chat_id, role, f"Message {i}")

        history = conversation.get_history(user_id, chat_id)

        # Должно остаться только 5 последних сообщений
        assert len(history) == max_messages
        assert history[0]["content"] == "Message 5"
        assert history[-1]["content"] == "Message 9"

    def test_max_history_limit_exact(self) -> None:
        """Тест когда количество сообщений ровно max_history_messages."""
        max_messages = 3
        conversation = Conversation(max_history_messages=max_messages)
        user_id, chat_id = 123, 456

        # Добавляем ровно max_messages сообщений
        conversation.add_message(user_id, chat_id, "user", "Message 1")
        conversation.add_message(user_id, chat_id, "assistant", "Message 2")
        conversation.add_message(user_id, chat_id, "user", "Message 3")

        history = conversation.get_history(user_id, chat_id)

        assert len(history) == max_messages

        # Добавляем еще одно - должно удалиться первое
        conversation.add_message(user_id, chat_id, "assistant", "Message 4")

        history = conversation.get_history(user_id, chat_id)
        assert len(history) == max_messages
        assert history[0]["content"] == "Message 2"
        assert history[-1]["content"] == "Message 4"

    def test_isolation_different_users(self) -> None:
        """Тест изоляции историй разных пользователей."""
        conversation = Conversation(max_history_messages=10)

        user1_id, chat1_id = 111, 222
        user2_id, chat2_id = 333, 444

        conversation.add_message(user1_id, chat1_id, "user", "User 1 message")
        conversation.add_message(user2_id, chat2_id, "user", "User 2 message")

        history1 = conversation.get_history(user1_id, chat1_id)
        history2 = conversation.get_history(user2_id, chat2_id)

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] == "User 1 message"
        assert history2[0]["content"] == "User 2 message"

    def test_isolation_same_user_different_chats(self) -> None:
        """Тест изоляции историй одного пользователя в разных чатах."""
        conversation = Conversation(max_history_messages=10)

        user_id = 123
        chat1_id = 111
        chat2_id = 222

        conversation.add_message(user_id, chat1_id, "user", "Chat 1 message")
        conversation.add_message(user_id, chat2_id, "user", "Chat 2 message")

        history1 = conversation.get_history(user_id, chat1_id)
        history2 = conversation.get_history(user_id, chat2_id)

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] == "Chat 1 message"
        assert history2[0]["content"] == "Chat 2 message"

    def test_chat_message_structure(self) -> None:
        """Тест структуры ChatMessage (TypedDict)."""
        conversation = Conversation(max_history_messages=10)
        user_id, chat_id = 123, 456

        conversation.add_message(user_id, chat_id, "user", "Test message")

        history = conversation.get_history(user_id, chat_id)
        message = history[0]

        # Проверяем что это dict с правильными ключами
        assert isinstance(message, dict)
        assert "role" in message
        assert "content" in message
        assert message["role"] == "user"
        assert message["content"] == "Test message"
