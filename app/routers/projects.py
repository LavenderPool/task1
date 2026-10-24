from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.routers.helpers import flush_or_409, get_object_or_404

router = APIRouter(prefix="/v1/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.id).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Project, project_id)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    flush_or_409(db, "project")
    db.commit()
    db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = get_object_or_404(db, Project, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    flush_or_409(db, "project")
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_object_or_404(db, Project, project_id)
    db.delete(project)
    flush_or_409(db, "project")
    db.commit()
