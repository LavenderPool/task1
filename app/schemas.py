from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

UserRole = Literal["operator", "admin"]
TaskStatus = Literal["open", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]


# ---------- users ----------


class UserCreate(BaseModel):
    email: str = Field(max_length=255)
    display_name: str = Field(min_length=1, max_length=255)
    role: UserRole = "operator"

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if "@" not in value or " " in value:
            raise ValueError("некорректный email")
        return value


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if "@" not in value or " " in value:
            raise ValueError("некорректный email")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    role: str
    created_at: datetime


# ---------- projects ----------


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime


# ---------- labels ----------


class LabelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    color: str = "#6b7280"

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if len(value) != 7 or value[0] != "#":
            raise ValueError("цвет должен быть в формате #RRGGBB")
        hex_part = value[1:]
        if not all(c in "0123456789abcdefABCDEF" for c in hex_part):
            raise ValueError("цвет должен быть в формате #RRGGBB")
        return value


class LabelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    color: str | None = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) != 7 or value[0] != "#":
            raise ValueError("цвет должен быть в формате #RRGGBB")
        hex_part = value[1:]
        if not all(c in "0123456789abcdefABCDEF" for c in hex_part):
            raise ValueError("цвет должен быть в формате #RRGGBB")
        return value


class LabelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str


# ---------- tasks ----------


class TaskCreate(BaseModel):
    project_id: int
    assignee_id: int | None = None
    label_id: int | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = "open"
    priority: TaskPriority = "medium"


class TaskUpdate(BaseModel):
    project_id: int | None = None
    assignee_id: int | None = None
    label_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    assignee_id: int | None
    label_id: int | None
    title: str
    description: str | None
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime


# ---------- comments ----------


class CommentCreate(BaseModel):
    task_id: int
    author_id: int
    body: str = Field(min_length=1)

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("текст комментария не может быть пустым")
        return value


class CommentUpdate(BaseModel):
    body: str | None = Field(default=None, min_length=1)

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("текст комментария не может быть пустым")
        return value


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    author_id: int
    body: str
    created_at: datetime
