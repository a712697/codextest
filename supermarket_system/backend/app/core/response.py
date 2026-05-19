from typing import Any


def success_response(data: Any, request_id: str) -> dict[str, Any]:
    return {"code": 0, "message": "success", "data": data, "request_id": request_id}


def error_response(code: int, message: str, request_id: str) -> dict[str, Any]:
    return {"code": code, "message": message, "data": None, "request_id": request_id}
