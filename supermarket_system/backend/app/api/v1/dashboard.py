from fastapi import APIRouter, Request

from app.core.response import success_response


router = APIRouter()


@router.get("")
def dashboard(request: Request):
    return success_response(
        {
            "sku_count": 0,
            "inventory_warning_count": 0,
            "today_stock_in_count": 0,
            "today_stock_out_count": 0,
        },
        request.state.request_id,
    )
