# rbac.py
from fastapi import HTTPException, status
from .models import User

def check_role(user: User, required_role: str):
    if user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions, must be {required_role}"
        )

def check_admin(user: User):
    check_role(user, "admin")

def check_guest(user: User):
    check_role(user, "guest")
