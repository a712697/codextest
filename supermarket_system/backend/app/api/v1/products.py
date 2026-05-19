from decimal import Decimal

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.response import success_response


router = APIRouter()


class ProductCreate(BaseModel):
    sku: str
    name: str
    price: Decimal = Field(ge=0)
    barcode: str | None = None
    min_stock: Decimal = Field(default=0, ge=0)


@router.post("")
def create_product(payload: ProductCreate, request: Request):
    # Wire to ProductService in implementation phase. SKU/barcode uniqueness belongs to DB + service layer.
    return success_response({"accepted": True, "product": payload.model_dump(mode="json")}, request.state.request_id)


@router.get("")
def list_products(request: Request, page: int = 1, page_size: int = 20, keyword: str | None = None):
    return success_response({"items": [], "total": 0, "page": page, "page_size": page_size, "keyword": keyword}, request.state.request_id)
