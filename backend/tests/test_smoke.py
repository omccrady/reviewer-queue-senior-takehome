import asyncio

import pytest
from fastapi import HTTPException

from app.main import ActionRequest, ITEMS, apply_action, health, list_review_items, reset_items


def run_async(coro):
    return asyncio.run(coro)


def test_health_check() -> None:
    assert run_async(health()) == {"status": "ok"}


def test_review_items_endpoint_returns_seed_data() -> None:
    response = run_async(list_review_items())
    assert len(response["items"]) > 0

def test_claim_action_updates_shared_item_state() -> None:
    run_async(reset_items())
    item_id = "RV-1031"

    response = run_async(apply_action(item_id, ActionRequest(action="claim", reviewer="alex")))

    assert response["item"]["status"] == "in_review"
    assert response["item"]["assigned_reviewer"] == "alex"


def test_approve_requires_item_to_be_in_review() -> None:
    run_async(reset_items())
    item_id = "RV-1031"

    with pytest.raises(HTTPException) as exc_info:
        run_async(apply_action(item_id, ActionRequest(action="approve", reviewer="alex")))

    assert exc_info.value.status_code == 409
    assert "cannot be approved" in str(exc_info.value.detail).lower()


def test_terminal_items_reject_further_actions() -> None:
    run_async(reset_items())
    item_id = "RV-1029"

    with pytest.raises(HTTPException) as exc_info:
        run_async(apply_action(item_id, ActionRequest(action="reject", reviewer="alex")))

    assert exc_info.value.status_code == 409
    assert "terminal" in str(exc_info.value.detail).lower()
