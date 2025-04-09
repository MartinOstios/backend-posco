from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers.login import router as login_router
from src.routers.enterprise import router as enterprise_router
from src.routers.employee import router as employee_router
from src.routers.role import router as role_router
from src.routers.permission import router as permission_router
from src.routers.category import router as category_router
from src.routers.supplier import router as supplier_router
from src.routers.product import router as product_router
from src.routers.client import router as client_router
from src.routers.invoice import router as invoice_router
from src.routers.sale import router as sale_router
from src.routers.notification import router as notification_router

from src.config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include all routers
app.include_router(login_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(enterprise_router, prefix=f"{settings.API_V1_STR}/enterprises", tags=["enterprises"])
app.include_router(employee_router, prefix=f"{settings.API_V1_STR}/employees", tags=["employees"])
app.include_router(role_router, prefix=f"{settings.API_V1_STR}/roles", tags=["roles"])
app.include_router(permission_router, prefix=f"{settings.API_V1_STR}/permissions", tags=["permissions"])
app.include_router(category_router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
app.include_router(supplier_router, prefix=f"{settings.API_V1_STR}/suppliers", tags=["suppliers"])
app.include_router(product_router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(client_router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
app.include_router(invoice_router, prefix=f"{settings.API_V1_STR}/invoices", tags=["invoices"])
app.include_router(sale_router, prefix=f"{settings.API_V1_STR}/sales", tags=["sales"])
app.include_router(notification_router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
