from fastapi import APIRouter, Request

from app.core.response import success_response

router = APIRouter()


@router.get("")
def list_stock_movements(request: Request, product_id: int | None = None):
    return success_response({"items": [], "product_id": product_id}, request.state.request_id)
