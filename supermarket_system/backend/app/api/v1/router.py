from fastapi import APIRouter

from app.api.v1 import (
    audit_logs,
    auth,
    brands,
    categories,
    dashboard,
    import_export,
    inventory,
    permissions,
    products,
    roles,
    stock_in,
    stock_movements,
    stock_out,
    suppliers,
    system_configs,
    users,
)


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["User"])
api_router.include_router(roles.router, prefix="/roles", tags=["Role"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permission"])
api_router.include_router(products.router, prefix="/products", tags=["Product"])
api_router.include_router(categories.router, prefix="/categories", tags=["Category"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brand"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["Supplier"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(stock_in.router, prefix="/stock-in", tags=["Stock In"])
api_router.include_router(stock_out.router, prefix="/stock-out", tags=["Stock Out"])
api_router.include_router(stock_movements.router, prefix="/stock-movements", tags=["Stock Movement"])
api_router.include_router(import_export.router, prefix="/import-export", tags=["Import Export"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Log"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(system_configs.router, prefix="/system-configs", tags=["System Config"])
