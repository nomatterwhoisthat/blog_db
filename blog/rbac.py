# rbac.py
from fastapi import HTTPException, status
from .models import User
from . import schemas

def check_role(user: User, required_role: str):
    if user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions, must be {required_role}"
        )
    return True

def check_admin(user: User):
    check_role(user, "admin")

def check_guest(user: User):
    check_role(user, "guest")

def check_moderator(user: schemas.User):
    if user.role != 'moderator':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action.")
