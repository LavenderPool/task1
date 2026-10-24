from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Коды ошибок PostgreSQL: уникальность и внешний ключ
PG_UNIQUE_VIOLATION = "23505"
PG_FOREIGN_KEY_VIOLATION = "23503"
PG_RESTRICT_VIOLATION = "23001"


def get_object_or_404(db: Session, model, obj_id: int):
    """Загружает объект по id или выбрасывает 404."""
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(
            status_code=404, detail=f"{model.__name__} with id {obj_id} not found"
        )
    return obj


def flush_or_409(db: Session, entity: str) -> None:
    """Фиксирует изменения; IntegrityError превращает в понятный 409."""
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        pgcode = getattr(exc.orig, "pgcode", None)
        if pgcode == PG_UNIQUE_VIOLATION:
            detail = f"{entity}: значение уже существует (нарушено ограничение уникальности)"
        if pgcode in (PG_FOREIGN_KEY_VIOLATION, PG_RESTRICT_VIOLATION):
            detail = f"{entity}: связанный объект не существует или используется (нарушен внешний ключ)"
        else:
            detail = f"{entity}: конфликт данных в базе"
        raise HTTPException(status_code=409, detail=detail) from exc
