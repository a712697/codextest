from fastapi import APIRouter, Request

from app.core.response import success_response

router = APIRouter()


@router.get("")
def list_brands(request: Request):
    return success_response({"items": []}, request.state.request_id)
