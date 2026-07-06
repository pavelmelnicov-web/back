from __future__ import annotations

import logging
from typing import Dict, List, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .data import COMMUNITY_POSTS, WORKBOOK
from .models import ChatMessage, ChatMessageCreate, WorkbookSession, WorkbookSessionCreate

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    ChatMessage(author="Space, Self.", message="Show us one thing you changed at home today."),
]


@app.get("/health")
def health() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/api/workbook")
def get_workbook() -> dict:
    logger.info("Workbook payload requested")
    return WORKBOOK


@app.post("/api/sessions", response_model=WorkbookSession)
def create_session(payload: WorkbookSessionCreate) -> WorkbookSession:
    logger.info(
        "Creating workbook session",
        extra={
            "name": payload.name,
            "version": payload.version,
            "situation_count": len(payload.situation_ids),
            "answer_count": len(payload.answers),
        },
    )
    session = WorkbookSession(**payload.model_dump())
    sessions[session.id] = session
    logger.info("Workbook session created", extra={"session_id": session.id})
    return session


@app.get("/api/sessions/{session_id}", response_model=WorkbookSession)
def get_session(session_id: str) -> WorkbookSession:
    logger.info("Fetching workbook session", extra={"session_id": session_id})
    session = sessions.get(session_id)
    if not session:
        logger.warning("Workbook session not found", extra={"session_id": session_id})
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/api/sessions/{session_id}/summary")
def get_summary(session_id: str) -> Dict[str, Union[str, List[str]]]:
    logger.info("Building workbook summary", extra={"session_id": session_id})
    session = sessions.get(session_id)
    if not session:
        logger.warning("Summary requested for missing session", extra={"session_id": session_id})
        raise HTTPException(status_code=404, detail="Session not found")

    answers = {item.step_id: item.answer for item in session.answers}
    version = next(item for item in WORKBOOK["versions"] if item["id"] == session.version)

    summary = {
        "title": "Personal space concept",
        "version": version["title"],
        "core_question": "What life do I want to live in this space?",
        "roles": answers.get("roles", "Roles not filled in yet"),
        "scenarios": answers.get("scenarios", "Scenarios not filled in yet"),
        "states": answers.get("states", "States not filled in yet"),
        "objects": answers.get("objects", "Objects not filled in yet"),
        "plan": answers.get("plan", "Plan not filled in yet"),
        "next_steps": [
            "choose one scenario that matters most to support",
            "remove objects that activate an old life",
            "add one object that supports the state you need",
        ],
    }
    logger.info("Workbook summary built", extra={"session_id": session_id, "title": summary["title"]})
    return summary


@app.get("/api/community")
def get_community() -> dict[str, list[dict[str, str]]]:
    logger.info("Community posts requested", extra={"post_count": len(COMMUNITY_POSTS)})
    return {"posts": COMMUNITY_POSTS}


@app.get("/api/chat", response_model=list[ChatMessage])
def list_chat_messages() -> list[ChatMessage]:
    logger.info("Chat messages requested", extra={"message_count": len(chat_messages)})
    return chat_messages[-25:]


@app.post("/api/chat", response_model=ChatMessage)
def create_chat_message(payload: ChatMessageCreate) -> ChatMessage:
    logger.info("Creating chat message", extra={"author": payload.author, "message_length": len(payload.message)})
    message = ChatMessage(**payload.model_dump())
    chat_messages.append(message)
    logger.info("Chat message created", extra={"message_id": message.id})
    return message
