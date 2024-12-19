from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, database, oauth2
from ..repository import notification

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

get_db = database.get_db

@router.get("/", response_model=List[schemas.ShowNotification])
def get_notifications_for_user(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    notifications = notification.get_notifications_for_user(current_user.id, db)
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found")
    return notifications



