from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.routers.helpers import flush_or_409, get_object_or_404

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    project_id: int | None = Query(default=None),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    if status_filter is not None:
        query = query.filter(Task.status == status_filter)
    return query.order_by(Task.id).all()


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Task, task_id)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    flush_or_409(db, "task")
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = get_object_or_404(db, Task, task_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    flush_or_409(db, "task")
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = get_object_or_404(db, Task, task_id)
    db.delete(task)
    flush_or_409(db, "task")
    db.commit()
