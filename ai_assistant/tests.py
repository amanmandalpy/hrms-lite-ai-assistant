from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import ChatSession, ChatMessage

User = get_user_model()


class ChatSessionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_employee",
            password="TestPass123!",
        )

    def test_chat_session_creation(self):
        session = ChatSession.objects.create(
            user=self.user,
            title="Leave Policy Questions",
        )

        self.assertEqual(session.user, self.user)
        self.assertEqual(session.title, "Leave Policy Questions")

    def test_default_chat_session_title(self):
        session = ChatSession.objects.create(
            user=self.user,
        )

        self.assertEqual(session.title, "New Chat")

    def test_chat_session_string_representation(self):
        session = ChatSession.objects.create(
            user=self.user,
            title="HR Questions",
        )

        self.assertEqual(
            str(session),
            "test_employee - HR Questions",
        )


class ChatMessageModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_employee",
            password="TestPass123!",
        )

        self.session = ChatSession.objects.create(
            user=self.user,
            title="Leave Policy Questions",
        )

    def test_user_message_creation(self):
        message = ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.Role.USER,
            content="How many casual leaves are available?",
        )

        self.assertEqual(message.session, self.session)
        self.assertEqual(message.role, "user")
        self.assertEqual(
            message.content,
            "How many casual leaves are available?",
        )

    def test_assistant_message_creation(self):
        message = ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.Role.ASSISTANT,
            content="Please check your HR leave policy.",
        )

        self.assertEqual(message.role, "assistant")

    def test_message_string_representation(self):
        message = ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.Role.USER,
            content="Hello",
        )

        self.assertEqual(
            str(message),
            "user - Leave Policy Questions",
        )

    def test_multiple_messages_in_one_session(self):
        ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.Role.USER,
            content="Hello",
        )

        ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.Role.ASSISTANT,
            content="Hello! How can I help?",
        )

        self.assertEqual(self.session.messages.count(), 2)

    def test_messages_deleted_with_session(self):
        ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.Role.USER,
            content="Hello",
        )

        self.session.delete()

        self.assertEqual(ChatMessage.objects.count(), 0)
