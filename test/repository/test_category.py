from unittest import TestCase
from unittest.mock import Mock
from fastapi import HTTPException
from blog import models, schemas
from blog.repository.category import create_category


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

    