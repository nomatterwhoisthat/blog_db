from unittest import TestCase
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException
from blog import models, schemas
from blog.repository.category import get_all_categories, create_category, get_blogs_by_category_name


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
        self.assertEqual(context.exception.detail, "Category not found")
        
        
    @patch("blog.repository.category.Session")
    def test_get_all_categories(self, mock_session):
        # Мокаем базу данных и query
        mock_db = mock_session.return_value
        mock_query = mock_db.query.return_value
        mock_query.all.return_value = [
            models.Category(id=1, name="Category 1"),
            models.Category(id=2, name="Category 2"),
        ]

        # Вызов функции
        result = get_all_categories(mock_db)

        # Проверки
        mock_db.query.assert_called_once_with(models.Category)
        mock_query.all.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Category 1")
        self.assertEqual(result[1].name, "Category 2")


    def test_create_category_no_name(self):
        # Создание запроса с пустым именем категории
        request = schemas.Category(name="")

        # Ожидаемое исключение HTTP 400
        with self.assertRaises(HTTPException) as context:
            create_category(request, self.db_mock)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Category name is required.")

