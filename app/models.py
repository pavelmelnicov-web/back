from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


WorkbookVersion = Literal["system", "atmosphere"]


class WorkbookAnswer(BaseModel):
    step_id: str = Field(min_length=2)
    answer: str = Field(min_length=1)


class WorkbookSessionCreate(BaseModel):
    name: str = Field(default="Guest", max_length=80)
    version: WorkbookVersion = "system"
    situation_ids: list[str] = Field(default_factory=list)
    answers: list[WorkbookAnswer] = Field(default_factory=list)


class WorkbookSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    version: WorkbookVersion
    situation_ids: list[str]
    answers: list[WorkbookAnswer]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessageCreate(BaseModel):
    author: str = Field(default="Guest", max_length=80)
    message: str = Field(min_length=1, max_length=500)


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    author: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
