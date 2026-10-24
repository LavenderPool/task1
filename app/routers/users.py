from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate
from app.routers.helpers import flush_or_409, get_object_or_404

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, User, user_id)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    flush_or_409(db, "user")
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = get_object_or_404(db, User, user_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    flush_or_409(db, "user")
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = get_object_or_404(db, User, user_id)
    db.delete(user)
    flush_or_409(db, "user")
    db.commit()
