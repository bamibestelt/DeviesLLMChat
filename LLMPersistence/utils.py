from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]]
    conversation_id: Optional[str]


class LLMStatus(BaseModel):
    status_code: int
    status_message: str


class LLMStatusCode(Enum):
    START = 0
    GET_RSS = 1
    PARSING = 2
    SAVING = 3
    FINISH = -1
    IDLE = -2


def get_llm_status_message(code):
    return {
        LLMStatusCode.START: "start",
        LLMStatusCode.GET_RSS: "fetching",
        LLMStatusCode.PARSING: "parsing",
        LLMStatusCode.SAVING: "saving",
        LLMStatusCode.FINISH: "finish",
        LLMStatusCode.IDLE: "idle",
    }.get(code, "unknown")


def get_llm_status(code: LLMStatusCode) -> dict:
    status = dict(
        status_code=code.value,
        status_message=get_llm_status_message(code)
    )
    return status