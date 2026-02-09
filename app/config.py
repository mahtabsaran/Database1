# app/config.py
from fastapi import FastAPI
from .db import create_db_and_tables  # تغییر این خط

# بقیه importها را هم باید اصلاح کنید:
from .routers import (
    provinces_router, city_router, village_router,
    factory_router, user_router, auth_router,
    measure_unit_router, pesticide_router, seed_router,
    crop_year_router, product_router, payment_reason_router,
    product_price_router, purity_price_router,
    farmer_router
)

app = FastAPI(
    title="HavirKesht Database",
    description=" *** Mahtab saran *** ",

    version="0.0.1",
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include all routers
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(provinces_router)
app.include_router(city_router)
app.include_router(village_router)
app.include_router(factory_router)
app.include_router(measure_unit_router)
app.include_router(pesticide_router)
app.include_router(seed_router)
app.include_router(crop_year_router)
app.include_router(product_router)
app.include_router(payment_reason_router)
app.include_router(product_price_router)
app.include_router(purity_price_router)
app.include_router(farmer_router)