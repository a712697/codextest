from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.response import success_response


router = APIRouter()


class StockOutItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class StockOutCreate(BaseModel):
    order_no: str
    reason: str
    items: list[StockOutItem]


@router.post("")
def create_stock_out(payload: StockOutCreate, request: Request):
    return success_response({"accepted": True, "order": payload.model_dump()}, request.state.request_id)


@router.post("/{order_id}/approve")
def approve_stock_out(order_id: int, request: Request):
    return success_response({"approved": True, "order_id": order_id}, request.state.request_id)
