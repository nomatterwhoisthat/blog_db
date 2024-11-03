from unittest import TestCase
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from blog import models, schemas
from blog.repository.comment import get_all_comments, create_comment, delete_comment
import json

class TestCommentFunctions(TestCase):

    # Тест функции получения всех комментариев
    def test_get_all_comments(self):
        db = Mock(spec=Session)
        
        # Настраиваем фиктивные комментарии для теста
        db.query(models.Comment).filter.return_value.all.return_value = [
            models.Comment(id=1, content="Комментарий 1", blog_id=1, user_id=1),
            models.Comment(id=2, content="Комментарий 2", blog_id=1, user_id=2)
        ]
        
        # Вызываем функцию и проверяем результат
        comments = get_all_comments(blog_id=1, db=db)
        self.assertEqual(len(comments), 2)  # Ожидаем 2 комментария
        self.assertEqual(comments[0].content, "Комментарий 1")

    # Тест функции создания нового комментария
    def test_create_comment(self):
        db = Mock(spec=Session)
        db.commit = Mock()  
        db.refresh = Mock()  
        
        # Настраиваем запрос комментария
        request = schemas.Comment(content="Новый комментарий")
        
        # Вызываем функцию и проверяем результат
        with patch.object(db, 'add', return_value=None) as mock_add:
            new_comment = create_comment(request, blog_id=1, user_id=1, db=db)
            mock_add.assert_called_once_with(new_comment)
            db.commit.assert_called_once()
            db.refresh.assert_called_once_with(new_comment)
            self.assertEqual(new_comment.content, "Новый комментарий")

    # Тест на отсутствие содержания в комментарии
    def test_create_comment_no_content(self):
        db = Mock(spec=Session)
        
        # Пустое содержание комментария должно вызывать ошибку
        request = schemas.Comment(content="")
        with self.assertRaises(HTTPException) as context:
            create_comment(request, blog_id=1, user_id=1, db=db)
        
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Comment content is required.")

    # Тест функции удаления комментария
    def test_delete_comment(self):
        db = Mock(spec=Session)
        db.commit = Mock()  # Имитируем commit
        
        # Настраиваем комментарий для теста
        comment = models.Comment(id=1, content="Комментарий", blog_id=1, user_id=1)
        db.query(models.Comment).filter.return_value.first.return_value = comment
        
        # Вызываем функцию и проверяем, что комментарий был удалён
        response = delete_comment(comment_id=1, db=db)  # Убираем user_id
        db.delete.assert_called_once_with(comment)
        db.commit.assert_called_once()
        
        # Декодируем тело JSON-ответа для проверки
        response_content = json.loads(response.body.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_content, {"detail": "Comment deleted successfully"})

    # Тест ошибки при попытке удаления несуществующего комментария
    def test_delete_comment_not_found(self):
        db = Mock(spec=Session)
        
        # Комментарий не найден
        db.query(models.Comment).filter.return_value.first.return_value = None
        with self.assertRaises(HTTPException) as context:
            delete_comment(comment_id=1, db=db)  # Убираем user_id
        
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "Comment not found.")
