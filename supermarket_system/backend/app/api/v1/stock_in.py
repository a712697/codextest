from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.response import success_response


router = APIRouter()


class StockInItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_cost_cents: int = Field(default=0, ge=0)


class StockInCreate(BaseModel):
    order_no: str
    supplier_id: int | None = None
    items: list[StockInItem]


@router.post("")
def create_stock_in(payload: StockInCreate, request: Request):
    return success_response({"accepted": True, "order": payload.model_dump()}, request.state.request_id)


@router.post("/{order_id}/approve")
def approve_stock_in(order_id: int, request: Request):
    return success_response({"approved": True, "order_id": order_id}, request.state.request_id)
