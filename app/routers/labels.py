from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Label
from app.schemas import LabelCreate, LabelRead, LabelUpdate
from app.routers.helpers import flush_or_409, get_object_or_404

router = APIRouter(prefix="/v1/labels", tags=["labels"])


@router.get("", response_model=list[LabelRead])
def list_labels(db: Session = Depends(get_db)):
    return db.query(Label).order_by(Label.id).all()


@router.get("/{label_id}", response_model=LabelRead)
def get_label(label_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Label, label_id)


@router.post("", response_model=LabelRead, status_code=status.HTTP_201_CREATED)
def create_label(payload: LabelCreate, db: Session = Depends(get_db)):
    label = Label(**payload.model_dump())
    db.add(label)
    flush_or_409(db, "label")
    db.commit()
    db.refresh(label)
    return label


@router.patch("/{label_id}", response_model=LabelRead)
def update_label(label_id: int, payload: LabelUpdate, db: Session = Depends(get_db)):
    label = get_object_or_404(db, Label, label_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(label, field, value)
    flush_or_409(db, "label")
    db.commit()
    db.refresh(label)
    return label


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(label_id: int, db: Session = Depends(get_db)):
    label = get_object_or_404(db, Label, label_id)
    db.delete(label)
    flush_or_409(db, "label")
    db.commit()
