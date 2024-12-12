from unittest import TestCase
from unittest.mock import Mock
from fastapi import HTTPException
from blog.repository.blog import create
from sqlalchemy.orm import Session

class TestCreateBlog(TestCase):

    def setUp(self):
        # Создаем фиктивную сессию базы данных
        self.db_mock = Mock(spec=Session)
        
        # Мокаем пользователя (например, администратор или обычный пользователь)
        self.current_user_mock = Mock()
        self.current_user_mock.id = 1  # ID текущего пользователя (можно настроить по вашему усмотрению)

    def test_create_without_title(self):
        # Создаем фиктивные данные для блога без заголовка
        blog_data = Mock()
        blog_data.title = ""  # Пустой заголовок
        blog_data.body = "Content of blog"
        blog_data.user_id = 1
        
        # Проверка, что при попытке создания блога без заголовка будет выброшено исключение
        with self.assertRaises(HTTPException) as context:
            create(self.db_mock, blog_data, current_user=self.current_user_mock)
        
        self.assertEqual(context.exception.status_code, 422)  # Ошибка 422 - Validation error
        self.assertEqual(context.exception.detail, "Title is required.")
        
    def test_create_without_body(self):
        # Создаем фиктивные данные для блога без тела
        blog_data = Mock()
        blog_data.title = "Blog with no body"
        blog_data.body = ""  # Пустое тело
        blog_data.user_id = 1
        
        # Проверка, что при попытке создания блога без тела будет выброшено исключение
        with self.assertRaises(HTTPException) as context:
            create(self.db_mock, blog_data, current_user=self.current_user_mock)
        
        self.assertEqual(context.exception.status_code, 422)  # Ошибка 422 - Validation error
        self.assertEqual(context.exception.detail, "String should have at least 1 character")
