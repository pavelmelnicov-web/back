from __future__ import annotations

from typing import Dict, List, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .data import COMMUNITY_POSTS, WORKBOOK
from .models import ChatMessage, ChatMessageCreate, WorkbookSession, WorkbookSessionCreate

app = FastAPI(title="Space, Self. API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, WorkbookSession] = {}
chat_messages: list[ChatMessage] = [
    ChatMessage(author="Space, Self.", message="Покажи, что ты изменил дома сегодня."),
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/workbook")
def get_workbook() -> dict:
    return WORKBOOK


@app.post("/api/sessions", response_model=WorkbookSession)
def create_session(payload: WorkbookSessionCreate) -> WorkbookSession:
    session = WorkbookSession(**payload.model_dump())
    sessions[session.id] = session
    return session


@app.get("/api/sessions/{session_id}", response_model=WorkbookSession)
def get_session(session_id: str) -> WorkbookSession:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/api/sessions/{session_id}/summary")
def get_summary(session_id: str) -> Dict[str, Union[str, List[str]]]:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answers = {item.step_id: item.answer for item in session.answers}
    version = next(item for item in WORKBOOK["versions"] if item["id"] == session.version)

    return {
        "title": "Личная концепция пространства",
        "version": version["title"],
        "core_question": "Какую жизнь я хочу жить в этом пространстве?",
        "roles": answers.get("roles", "Роли пока не заполнены"),
        "scenarios": answers.get("scenarios", "Сценарии пока не заполнены"),
        "states": answers.get("states", "Состояния пока не заполнены"),
        "objects": answers.get("objects", "Предметы пока не заполнены"),
        "plan": answers.get("plan", "План пока не заполнен"),
        "next_steps": [
            "выбрать один сценарий, который важнее всего поддержать",
            "убрать предметы, которые включают старую жизнь",
            "добавить один объект, который помогает нужному состоянию",
        ],
    }


@app.get("/api/community")
def get_community() -> dict[str, list[dict[str, str]]]:
    return {"posts": COMMUNITY_POSTS}


@app.get("/api/chat", response_model=list[ChatMessage])
def list_chat_messages() -> list[ChatMessage]:
    return chat_messages[-25:]


@app.post("/api/chat", response_model=ChatMessage)
def create_chat_message(payload: ChatMessageCreate) -> ChatMessage:
    message = ChatMessage(**payload.model_dump())
    chat_messages.append(message)
    return message
