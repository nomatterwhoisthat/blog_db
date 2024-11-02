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

    def test_create_category_success(self):
        # Подготавливаем запрос на создание категории
        request = schemas.Category(name="NewCategory")

        # Устанавливаем, что категории с таким именем не существует
        self.db_mock.query().filter().first.return_value = None

        # Вызов функции и проверка результата
        result = create_category(request, self.db_mock)
        self.assertEqual(result.name, "NewCategory")
        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once_with(result)

    def test_create_category_no_name(self):
        # Создание запроса с пустым именем категории
        request = schemas.Category(name="")

        # Ожидаемое исключение HTTP 400
        with self.assertRaises(HTTPException) as context:
            create_category(request, self.db_mock)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Category name is required.")

    def test_create_category_name_already_exists(self):
        # Создание запроса с именем существующей категории
        request = schemas.Category(name="ExistingCategory")

        # Устанавливаем, что категория с таким именем уже существует
        self.db_mock.query().filter().first.return_value = models.Category(id=1, name="ExistingCategory")

        # Ожидаемое исключение HTTP 400
        with self.assertRaises(HTTPException) as context:
            create_category(request, self.db_mock)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Category already exists.")

    def test_get_blogs_by_category_name_success(self):
        # Создание категории с блогами
        blog1 = models.Blog(id=1, title="Blog1", body="Content1")
        blog2 = models.Blog(id=2, title="Blog2", body="Content2")
        category = models.Category(id=1, name="CategoryWithBlogs", blogs=[blog1, blog2])

        # Возвращаем категорию при запросе по имени
        self.db_mock.query().filter().first.return_value = category

        # Вызов функции и проверка результата
        result = get_blogs_by_category_name("CategoryWithBlogs", self.db_mock)
        self.assertEqual(result, [blog1, blog2])

    def test_get_blogs_by_category_name_not_found(self):
        # Устанавливаем, что категория не найдена
        self.db_mock.query().filter().first.return_value = None

        # Ожидаемое исключение HTTP 404
        with self.assertRaises(HTTPException) as context:
            get_blogs_by_category_name("NonExistentCategory", self.db_mock)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Category not found")
