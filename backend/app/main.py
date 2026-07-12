from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "review_items.json"

ReviewAction = Literal["claim", "approve", "reject", "escalate"]


class ActionRequest(BaseModel):
    action: ReviewAction
    reviewer: str = "alex"


app = FastAPI(title="Reviewer Queue API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_seed_items() -> list[dict]:
    with DATA_FILE.open() as file:
        return json.load(file)


ITEMS = load_seed_items()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/dev/reset")
async def reset_items() -> dict:
    global ITEMS
    ITEMS = load_seed_items()
    return {"items": deepcopy(ITEMS)}


@app.get("/review-items")
async def list_review_items(active_only: bool = True) -> dict:
    items = deepcopy(ITEMS)

    if active_only:
        items = [item for item in items if item["status"] not in {"approved", "rejected", "escalated"}]

    items.sort(key=lambda item: item["submitted_at"], reverse=True)
    return {"items": items}


@app.get("/review-items/{item_id}")
async def get_review_item(item_id: str) -> dict:
    item = find_item(item_id)
    return {"item": deepcopy(item)}


@app.post("/review-items/{item_id}/actions")
async def apply_action(item_id: str, request: ActionRequest) -> dict:

    item_index = next(
        (index for index, item in enumerate(ITEMS) if item["id"] == item_id),
        None,
    )
    if item_index is None:
        raise HTTPException(status_code=404, detail="Review item not found")

    item = ITEMS[item_index]
    current_status = item["status"]
    terminal_states = {"approved", "rejected", "escalated"}

    if request.action == "claim":
        if current_status in terminal_states:
            raise HTTPException(status_code=409, detail="This item is in a terminal state and cannot be claimed")
        if current_status == "in_review":
            raise HTTPException(status_code=409, detail="This item is already being reviewed")
        item["status"] = "in_review"
        item["assigned_reviewer"] = request.reviewer
    elif request.action in {"approve", "reject", "escalate"}:
        if current_status in terminal_states:
            raise HTTPException(status_code=409, detail="This item is already in a terminal state")
        if current_status != "in_review":
            raise HTTPException(status_code=409, detail="This item cannot be approved until it is claimed")
        item["status"] = status_for_action(request.action)
        if request.action == "approve":
            item["assigned_reviewer"] = item.get("assigned_reviewer") or request.reviewer
    else:
        raise HTTPException(status_code=400, detail="Unsupported action")

    ITEMS[item_index] = item
    return {"item": deepcopy(item)}


def find_item(item_id: str) -> dict:
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Review item not found")


def status_for_action(action: ReviewAction) -> str:
    if action == "approve":
        return "approved"
    if action == "reject":
        return "rejected"
    if action == "escalate":
        return "escalated"
    return "in_review"
