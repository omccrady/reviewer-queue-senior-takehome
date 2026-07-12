import asyncio

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
