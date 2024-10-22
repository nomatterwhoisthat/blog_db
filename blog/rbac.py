# from fastapi import Depends, HTTPException, status
# from . import models, database
# from sqlalchemy.orm import Session
# from .oauth2 import get_current_user

# def get_current_user_role(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
#     user = db.query(models.User).filter(models.User.id == current_user.id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return user.role

# def require_role(required_role: str):
#     def role_checker(db: Session = Depends(database.get_db), current_user_role: str = Depends(get_current_user_role)):
#         if current_user_role != required_role:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"User does not have access to this resource. Required role: {required_role}"
#             )
#     return role_checker

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from . import oauth2

class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user = await oauth2.get_current_user(request)
        
        if user.role == 'admin':
            # Разрешить всем действиям для администратора
            response = await call_next(request)
            return response
        elif user.role == 'guest':
            # Ограничиваем действия для гостя
            if request.method in ['DELETE', 'PUT']:
                raise HTTPException(status_code=403, detail="Access denied for guests")
        
        response = await call_next(request)
        return response

