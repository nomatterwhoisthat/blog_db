from sqlalchemy.orm import Session
from .. import models

def create_notification(user_id: int, content: str, db: Session):
    notification = models.Notification(user_id=user_id, content=content)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_notifications_for_user(user_id: int, db: Session):
    # Получаем все уведомления для пользователя по его ID
    notifications = db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
    return notifications

