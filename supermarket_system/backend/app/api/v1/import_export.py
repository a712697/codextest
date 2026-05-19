from fastapi import APIRouter, Request, UploadFile

from app.core.response import success_response

router = APIRouter()


@router.post("/products")
def import_products(file: UploadFile, request: Request):
    return success_response({"accepted": True, "filename": file.filename, "errors": []}, request.state.request_id)


@router.get("/products")
def export_products(request: Request):
    return success_response({"download_url": None}, request.state.request_id)
