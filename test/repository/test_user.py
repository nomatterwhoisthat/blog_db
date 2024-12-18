from unittest import TestCase
from unittest.mock import Mock, patch
from blog.models import User
from blog.schemas import User as UserSchema
from blog.repository.user import create, show, destroy_user
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class TestUserFunctions(TestCase):

    def setUp(self):
        # Мокаем базу данных и модель пользователя
        self.db_mock = Mock()
        self.mock_user = User(id=1, name="TestUser", email="test@example.com", password="hashedpassword")
        
    @patch('blog.hashing.Hash.bcrypt', return_value="hashedpassword")
    def test_create_user_success(self, mock_bcrypt):
        request = UserSchema(name="NewUser", email="new@example.com", password="Secure123")
        
        # Настройка, чтобы запросы на уникальность имени и email возвращали None 
        # (если возращает None, то пользователя не существует)
        self.db_mock.query().filter().first.return_value = None

        new_user = create(request, self.db_mock)
        
        # Проверка, что данные пользователя были установлены правильно
        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once()
        self.assertEqual(new_user.name, request.name)
        self.assertEqual(new_user.email, request.email)
        self.assertEqual(new_user.password, "hashedpassword")

    def test_create_user_name_taken(self):
        request = UserSchema(name="TestUser", email="unique@example.com", password="Secure123")
        
        # Имя пользователя уже существует
        self.db_mock.query().filter().first.side_effect = [self.mock_user, None]
        # проверка исключений и вызов функции 
        with self.assertRaises(HTTPException) as context:
            create(request, self.db_mock)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "The name is taken. Choose the another one.")

    def test_create_user_email_taken(self):
        request = UserSchema(name="UniqueName", email="test@example.com", password="Secure123")
        
        # Email уже существует
        self.db_mock.query().filter().first.side_effect = [None, self.mock_user]

        with self.assertRaises(HTTPException) as context:
            create(request, self.db_mock)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Email already registered")

    def test_show_user_success(self):
        # Настройка, чтобы запрос пользователя по id возвращал пользователя
        self.db_mock.query().filter().first.return_value = self.mock_user

        user = show(1, self.db_mock)
        self.assertEqual(user.id, self.mock_user.id)
        self.assertEqual(user.name, self.mock_user.name)
        self.assertEqual(user.email, self.mock_user.email)

    def test_show_user_not_found(self):
        # Настройка, чтобы запрос пользователя по id возвращал None (не найден)
        self.db_mock.query().filter().first.return_value = None

        with self.assertRaises(HTTPException) as context:
            show(1, self.db_mock)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User with the id 1 is not available")

    def test_destroy_user_success(self):
        # Настройка, чтобы запрос пользователя по id возвращал пользователя
        self.db_mock.query().filter().first.return_value = self.mock_user

        response = destroy_user(1, 1, self.db_mock)
        self.db_mock.delete.assert_called_once_with(self.mock_user)
        self.db_mock.commit.assert_called_once()
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'{"detail":"Blog deleted successfully."}')

    def test_destroy_user_not_found(self):
        # Настройка, чтобы запрос пользователя по id возвращал None (не найден)
        self.db_mock.query().filter().first.return_value = None

        with self.assertRaises(HTTPException) as context:
            destroy_user(1, 1, self.db_mock)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found.")