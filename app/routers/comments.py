from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Comment
from app.schemas import CommentCreate, CommentRead, CommentUpdate
from app.routers.helpers import flush_or_409, get_object_or_404

router = APIRouter(prefix="/v1/comments", tags=["comments"])


@router.get("", response_model=list[CommentRead])
def list_comments(
    task_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Comment)
    if task_id is not None:
        query = query.filter(Comment.task_id == task_id)
    return query.order_by(Comment.id).all()


@router.get("/{comment_id}", response_model=CommentRead)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Comment, comment_id)


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentCreate, db: Session = Depends(get_db)):
    comment = Comment(**payload.model_dump())
    db.add(comment)
    flush_or_409(db, "comment")
    db.commit()
    db.refresh(comment)
    return comment


@router.patch("/{comment_id}", response_model=CommentRead)
def update_comment(comment_id: int, payload: CommentUpdate, db: Session = Depends(get_db)):
    comment = get_object_or_404(db, Comment, comment_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(comment, field, value)
    flush_or_409(db, "comment")
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = get_object_or_404(db, Comment, comment_id)
    db.delete(comment)
    flush_or_409(db, "comment")
    db.commit()
