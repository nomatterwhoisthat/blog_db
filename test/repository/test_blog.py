from unittest import TestCase
from unittest.mock import Mock
from blog.repository.blog import get_all, sort_blogs_by_length
from blog.models import Blog
from sqlalchemy.orm import Session
from fastapi import HTTPException

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
