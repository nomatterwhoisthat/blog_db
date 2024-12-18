from unittest import TestCase
from blog.repository.blog import get_all, sort_blogs_by_length, create
from blog.schemas import BlogBase
from unittest import TestCase
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from blog.models import Blog, User, Category
from blog.routers.blog import update_blog, destroy, create
import json
from blog.repository.blog import sort_blogs_by_length
from sqlalchemy.orm import Session
from pydantic import ValidationError

class TestGetAllBlogs(TestCase):
    def test_get_all_returns_blogs(self):
        # Создаем фиктивную сессию базы данных
        db_mock = Mock()

        # Создаем фиктивные данные для модели Blog
        blog1 = Blog(id=1, title="Blog 1", body="Content of blog 1", user_id=1)
        blog2 = Blog(id=2, title="Blog 2", body="Content of blog 2", user_id=2)
        db_mock.query.return_value.all.return_value = [blog1, blog2]

        # Вызываем функцию get_all с фиктивной сессией базы данных
        result = get_all(db_mock)

        # Проверяем, что функция возвращает правильные данные
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "Blog 1")
        self.assertEqual(result[1].title, "Blog 2")

        # Проверяем, что функция использовала метод query и all
        db_mock.query.assert_called_once_with(Blog)
        db_mock.query.return_value.all.assert_called_once()
        
class TestSortBlogsByLength(TestCase):

    def setUp(self):
        # Создаем фиктивные данные для блогов
        self.blog1 = Blog(id=1, title="Blog 1", body="Short", user_id=1)
        self.blog2 = Blog(id=2, title="Blog 2", body="A bit longer content", user_id=2)
        self.blog3 = Blog(id=3, title="Blog 3", body="This is the longest blog content here", user_id=3)
        
        # Создаем фиктивную сессию базы данных
        self.db_mock = Mock(spec=Session)

    def test_invalid_sort_order(self):
        # Проверка на исключение для некорректного значения параметра сортировки
        with self.assertRaises(HTTPException) as context:
            sort_blogs_by_length(self.db_mock, sort_order="invalid")
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Invalid sort order. Use 'asc', 'desc', or omit it.")

    def test_sort_asc(self):
        # Мокаем результат запроса, возвращая блоги в случайном порядке
        self.db_mock.query.return_value.order_by.return_value.all.return_value = [self.blog1, self.blog2, self.blog3]

        result = sort_blogs_by_length(self.db_mock, sort_order="asc")

        # Проверка, что блоги отсортированы по возрастанию длины
        expected_lengths = [len(self.blog1.body), len(self.blog2.body), len(self.blog3.body)]
        self.assertEqual([blog['length'] for blog in result], expected_lengths)

    def test_sort_desc(self):
        # Мокаем результат запроса, возвращая блоги в случайном порядке
        self.db_mock.query.return_value.order_by.return_value.all.return_value = [self.blog3, self.blog2, self.blog1]

        result = sort_blogs_by_length(self.db_mock, sort_order="desc")

        # Проверка, что блоги отсортированы по убыванию длины
        expected_lengths = [len(self.blog3.body), len(self.blog2.body), len(self.blog1.body)]
        self.assertEqual([blog['length'] for blog in result], expected_lengths)

    def test_no_sort_order(self):
        # Мокаем результат запроса без сортировки
        self.db_mock.query.return_value.all.return_value = [self.blog1, self.blog2, self.blog3]

        result = sort_blogs_by_length(self.db_mock)

        # Проверка, что блоги возвращены в исходном порядке
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['title'], "Blog 1")
        self.assertEqual(result[1]['title'], "Blog 2")
        self.assertEqual(result[2]['title'], "Blog 3")


class TestBlogOperations(TestCase):
    def setUp(self):
        # Создание мока для сессии базы данных
        self.db_mock = Mock(spec=Session) 
        # Создание пользователей с разными ролями
        self.user_1 = User(id=1, name="user1", email="user1@example.com", password="Password123", role="user")
        self.user_2 = User(id=2, name="user2", email="user2@example.com", password="Password123", role="user")
        self.admin_user = User(id=99, name="admin", email="admin@example.com", password="Admin123", role="admin")

        # Создание блогов, принадлежащих различным пользователям
        self.blog_1 = Blog(id=1, title="Blog 1", body="Content of blog 1", user_id=1)
        self.blog_2 = Blog(id=2, title="Blog 2", body="Content of blog 2", user_id=2)

        # Мокаем поведение метода db.query().filter().first(), чтобы возвращать определенные блоги по ID
        self.db_mock.query.return_value.filter.return_value.first.side_effect = [
            self.blog_1,  # Для запроса блога с ID 1 возвращается первый блог
            self.blog_2,  # Для запроса блога с ID 2 возвращается второй блог
            None  # Для запросов с несуществующими ID будет возвращаться None
        ]
        
        # Мокаем категории (предполагаем, что категории — это список)
        category_mock = MagicMock(spec=Category)
        category_mock._sa_instance_state = MagicMock()  # Мокаем _sa_instance_state для модели Category
        self.db_mock.query.return_value.filter.return_value.all.return_value = [category_mock]
        
    def test_create_blog_without_title(self):
        # Попытка создать блог без заголовка
        blog_data = {
            "title": "",  # Пустой заголовок
            "body": "This is a body of the blog",  # Тело блога
            "photo_id": 0,  # ID фото
            "category_names": ["Category1"]  # Название категории
        }

        with self.assertRaises(HTTPException) as context:
            # Передаем пустое значение заголовка в схему BlogBase
            request = BlogBase(**blog_data)
            create(request, self.db_mock, current_user=self.user_1)  # Пользователь 1 пытается создать блог без заголовка
        # Проверяем, что возникло исключение с нужным сообщением
        self.assertEqual(context.exception.status_code, 400)  # Ожидаем статус 400 (Bad Request)
        self.assertEqual(context.exception.detail, "Title is required.")  # Ожидаем сообщение об ошибке
     
    def test_create_blog_without_body(self):
        # Попытка создать блог без тела
        blog_data = {
            "title": "Test Blog Without Body",  # Заголовок блога
            "body": "",  # Пустое тело блога
            "category_names": ["Category1"],  # Название категории
            "photo_id": 0  # ID фото
        }

        with self.assertRaises(ValidationError) as context:
            # Передаем пустое значение тела блога в схему BlogBase
            request = BlogBase(**blog_data)
            # Попытка создать блог с пустым телом
            create(request, self.db_mock, current_user=self.user_1)  # Пользователь 1 пытается создать блог без тела

        # Проверяем, что возникло исключение с нужным сообщением
        self.assertIn("String should have at least 1 character", str(context.exception))  # Сообщение об ошибке

   
    def test_delete_blog_not_author(self):
        # Тестируем удаление блога пользователем, который не является его автором
        with self.assertRaises(HTTPException) as context:
            destroy(1, self.db_mock, current_user=self.user_2)  # Пользователь 2 пытается удалить блог 1
        self.assertEqual(context.exception.status_code, 403)  # Ожидаем статус 403 (Forbidden)
        self.assertEqual(context.exception.detail, "Insufficient permissions, must be admin or the owner of the blog.")  # Ожидаем сообщение о недостаточных правах

    def test_delete_blog_success(self):
        # Тестируем успешное удаление блога автором (пользователь 1)
        result = destroy(1, self.db_mock, current_user=self.user_1)  # Пользователь 1 удаляет свой блог 1
        
        # Проверяем статус ответа и содержимое
        self.assertEqual(result.status_code, 200)  # Ожидаем статус 200 (OK)
        response_content = result.body.decode()  # Декодируем тело ответа
        self.assertEqual(response_content, '{"detail":"Blog deleted successfully"}')  # Ожидаем сообщение о успешном удалении блога

    def test_delete_blog_by_admin(self):
        # Тестируем удаление блога администратором
        result = destroy(2, self.db_mock, current_user=self.admin_user)  # Администратор удаляет блог 2
        
        # Проверяем статус ответа и содержимое
        self.assertEqual(result.status_code, 200)  # Ожидаем статус 200 (OK)
        response_content = result.body.decode()  # Декодируем тело ответа
        self.assertEqual(response_content, '{"detail":"Blog deleted successfully"}')  # Ожидаем сообщение о успешном удалении блога

    def test_update_blog_success(self):
        # Тестируем успешное обновление блога с существующим ID
        blog_data = {
            "title": "Updated Blog Title",  # Обновленный заголовок
            "body": "Updated body content for the blog",  # Обновленное содержание
            "photo_id": 0,  # ID фото
            "category_names": ["Category1"]  # Название категории
        }
        
        # Создаем объект запроса на основе схемы BlogBase
        request = BlogBase(**blog_data)
        
        # Вызываем функцию обновления блога с мокданными
        result = update_blog(1, request, self.db_mock, current_user=self.user_1)  # Пользователь 1 обновляет свой блог 1
        
        # Проверяем статус ответа
        self.assertEqual(result.status_code, 200)  # Ожидаем статус 200 (OK)
        
        # Декодируем тело ответа в формате JSON
        response_content = json.loads(result.body.decode())
        
        # Проверяем, что ответ содержит сообщение об успешном обновлении блога
        self.assertEqual(response_content, {"detail": "Blog updated successfully"})

    def test_update_blog_not_author(self):
        # Тестируем обновление блога пользователем, который не является его автором
        with self.assertRaises(HTTPException) as context:
            request = BlogBase(title="New Title", body="New Body", photo_id=0, category_names=["Category1"])
            update_blog(1, request, self.db_mock, current_user=self.user_2)  # Пользователь 2 пытается обновить блог 1, которому он не принадлежит
        
        self.assertEqual(context.exception.status_code, 403)  # Ожидаем статус 403 (Forbidden)
        self.assertEqual(context.exception.detail, "You are not authorized to update this blog.")  # Ожидаем сообщение о недопустимости изменения чужого блога

    

    def test_create_blog_without_categories_and_photo(self):
        # Попытка создать блог без категорий и фото
        blog_data = {
            "title": "Test.",
            "body": "I test my app and it's cool.",
            "category_names": [""],  # Пустой список категорий
            "photo_id": None  # Нет фото
        }

        # Мокаем категории как пустой список
        self.db_mock.query.return_value.filter.return_value.all.return_value = []

        # Создаем блог с мокданными
        request = BlogBase(**blog_data)
        new_blog = create(request, self.db_mock, current_user=self.user_1)

        # Проверяем, что блог был создан
        self.assertIsNotNone(new_blog)
        self.assertEqual(new_blog.title, "Test.")  # Проверяем заголовок
        self.assertEqual(new_blog.body, "I test my app and it's cool.")  # Проверяем содержание
        
        # Проверяем, что категории пусты и фото не добавлено
        self.assertEqual(new_blog.categories, [])
        self.assertEqual(new_blog.photo_id, None)

