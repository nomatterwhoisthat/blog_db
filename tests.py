from unittest import TestCase
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from blog.models import Blog, User, Category
from blog.routers.blog import update_blog, destroy, create
from blog.schemas import BlogBase
import json
from blog.repository.blog import sort_blogs_by_length, show
from blog.repository.category import create_category, get_blogs_by_category_name
from sqlalchemy.orm import Session
from blog import models, schemas
from pydantic import ValidationError

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


class TestSortBlogsByLength(TestCase):

    def setUp(self):
        # Инициализация тестовых данных
        self.blog1 = Blog(id=1, title="Blog 1", body="Short", user_id=1)
        self.blog2 = Blog(id=2, title="Blog 2", body="A bit longer content", user_id=2)
        self.blog3 = Blog(id=3, title="Blog 3", body="This is the longest blog content here", user_id=3)
        self.db_mock = Mock(spec=Session)

    def test_sort_asc(self):
        # Проверяем сортировку по возрастанию длины контента
        self.db_mock.query.return_value.order_by.return_value.all.return_value = [self.blog1, self.blog2, self.blog3]
        result = sort_blogs_by_length(self.db_mock, sort_order="asc")
        expected_lengths = [len(self.blog1.body), len(self.blog2.body), len(self.blog3.body)]
        self.assertEqual([blog['length'] for blog in result], expected_lengths)

    def test_invalid_sort_order(self):
        with self.assertRaises(HTTPException) as context:
            sort_blogs_by_length(self.db_mock, sort_order="ascdesc")
        self.assertEqual(context.exception.status_code, 400)  # Ожидаем статус 400 (Bad Request)
        self.assertEqual(context.exception.detail, "Invalid sort order. Use 'asc', 'desc', or omit it.")  # Ожидаем сообщение об ошибке

   
    def test_sort_desc(self):
        # Проверяем сортировку по убыванию длины контента
        self.db_mock.query.return_value.order_by.return_value.all.return_value = [self.blog3, self.blog2, self.blog1]
        result = sort_blogs_by_length(self.db_mock, sort_order="desc")
        expected_lengths = [len(self.blog3.body), len(self.blog2.body), len(self.blog1.body)]
        self.assertEqual([blog['length'] for blog in result], expected_lengths)

    def test_no_sort_order(self):
        # Проверяем результат без указания порядка сортировки
        self.db_mock.query.return_value.all.return_value = [self.blog1, self.blog2, self.blog3]
        result = sort_blogs_by_length(self.db_mock)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['title'], "Blog 1")
        self.assertEqual(result[1]['title'], "Blog 2")
        self.assertEqual(result[2]['title'], "Blog 3")

class TestShowBlog(TestCase):
    def setUp(self):
        # Мокаем сессию базы данных
        self.db_mock = Mock(spec=Session)

        # Создание блогов
        self.blog_6 = Blog(id=6, title="Blog 6", body="Content of blog 6", user_id=1)

        # Мокаем запрос для существующего блога с ID 6 и несуществующего с ID 26
        self.db_mock.query.return_value.filter.return_value.first.side_effect = [
            self.blog_6,  # Блог с ID 6
        ]

    def test_show_blog_with_id(self):
        # Проверяем получение информации о блоге с существующим ID (6)
        result = show(6, self.db_mock)

        # Проверяем, что информация о блоге с ID 6 получена корректно
        self.assertEqual(result.id, 6)
        self.assertEqual(result.title, "Blog 6")
        self.assertEqual(result.body, "Content of blog 6")

    


class TestCategoryFunctions(TestCase):
    def setUp(self):
        # Создание фиктивной сессии базы данных
        self.db_mock = Mock()
        
    # Тест 1: Создание новой категории "Cakes"
    def test_create_category_cakes_success(self):
        request = schemas.Category(name="Cakes")
        
        # Устанавливаем, что категории с таким именем нет
        self.db_mock.query().filter().first.return_value = None

        # Вызов функции и проверка результата
        result = create_category(request, self.db_mock)
        self.assertEqual(result.name, "Cakes")
        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once_with(result)

    # Тест 2: Попытка создать категорию "Cakes", которая уже существует
    def test_create_category_cakes_exists(self):
        request = schemas.Category(name="Cakes")
        
        # Устанавливаем, что категория с таким именем уже существует
        self.db_mock.query().filter().first.return_value = models.Category(id=1, name="Cakes")

        # Ожидаемое исключение HTTP 400
        with self.assertRaises(HTTPException) as context:
            create_category(request, self.db_mock)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Category already exists.")

    # Тест 3: Получение списка блогов по существующей категории "Education"
    def test_get_blogs_by_category_name_education_success(self):
        # Создание категории с блогами
        blog1 = models.Blog(id=1, title="Blog1", body="Content1")
        blog2 = models.Blog(id=2, title="Blog2", body="Content2")
        category = models.Category(id=1, name="Education", blogs=[blog1, blog2])

        # Возвращаем категорию при запросе по имени
        self.db_mock.query().filter().first.return_value = category

        # Вызов функции и проверка результата
        result = get_blogs_by_category_name("Education", self.db_mock)
        self.assertEqual(result, [blog1, blog2])

    # Тест 4: Получение списка блогов по несуществующей категории "univer"
    def test_get_blogs_by_category_name_univer_not_found(self):
        # Устанавливаем, что категория не найдена
        self.db_mock.query().filter().first.return_value = None

        # Ожидаемое исключение HTTP 404
        with self.assertRaises(HTTPException) as context:
            get_blogs_by_category_name("univer", self.db_mock)
        self.assertEqual(context.exception.status_code, 404)


