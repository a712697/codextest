from fastapi import APIRouter, Request

from app.core.response import success_response


router = APIRouter()


@router.get("")
def list_inventory(request: Request, page: int = 1, page_size: int = 20):
    return success_response({"items": [], "total": 0, "page": page, "page_size": page_size}, request.state.request_id)


@router.get("/warnings")
def inventory_warnings(request: Request):
    return success_response({"items": []}, request.state.request_id)
