مرحله1:از طریق محیطSwaggerهمهAPIهای سمت سرور بررسی شده و هر کدام تست شوند. در گام اول
لیست همهAPIها در یک جدولشامل نام، ورودی، خروجی و ...مستند سازی شود.
این مرحله در یک فایل word جداگانه قرار گرفته است و در آن لیست همه جداول را قرار داده ام .
----

مرحله2:همه صفحات سمت کاربر بررسی شود و مشخص کنید هر صفحه کدامAPIرا فراخوانی میکند.در این
مرحله تسلط کافیبرتب های مختلفInspectمرورگر الزم است.

تمام صفحات زیر بررسی شدند:

صفحه ورود:
صفحه اصلی: 
ثبت سال زراعی: 
ثبت استان:
ثبت شهرستان: ![Uploading image.png…]()
ثبت روستا ![Uploading image.png…]()



____________________________________________________________________________________________________________________________________________________________________________________________

مرحله3:لیست همه جداول،فیلدهای هر جدول وارتباطات بینجداولدر اختیار شما قرار داده می شود.یکپایگاه
دادهرابطه ایرا پیاده سازی کنید..

---

**گزارش مرحله ۳ – پیاده‌سازی پایگاه داده رابطه‌ای با SQLAlchemy و SQLite**

**روش انجام:**  
به‌جای ایجاد دستی جداول یا استفاده از ORM سبک‌تر مانند Peewee، از **SQLAlchemy ORM** به‌صورت **declarative base** استفاده شده است. پایگاه داده **SQLite** به‌عنوان موتور ذخیره‌سازی به‌کار رفته و تمامی تنظیمات بهینه‌سازی برای کار در محیط وب و دسترسی همزمان اعمال شده است.

**گام‌های انجام‌شده:**

1. **اتصال به SQLite با تنظیمات پیشرفته:**
   - فایل دیتابیس `database.db` در مسیر نسبی تعیین شده است.
   - تنظیمات اتصال شامل `check_same_thread=False` برای قابلیت استفاده در محیط چندنخی FastAPI، افزایش `timeout` و تنظیم `isolation_level` به `None` برای عملکرد بهتر.

2. **فعال‌سازی قابلیت‌های پیشرفته SQLite:**
   - با استفاده از `event.listens_for`، در زمان اتصال، **PRAGMA**های مهم فعال شده‌اند:
     - `foreign_keys=ON` برای فعال‌سازی یکپارچگی کلید خارجی
     - `journal_mode=WAL` برای پشتیبانی بهتر از دسترسی همزمان (concurrent access)
     - `busy_timeout=5000` برای کاهش خطای قفل دیتابیس

3. **تعریف مدل‌ها با declarative_base:**
   - مدل‌های دیتابیس (مانند `User`, `Farm`, `Product` و غیره) به‌صورت کلاس‌های Python و با استفاده از `Base = declarative_base()` تعریف شده‌اند.
   - هر مدل شامل فیلدها، نوع داده‌ها، روابط و محدودیت‌ها بوده است.

4. **ایجاد خودکار جداول:**
   - تابع `create_db_and_tables()` با فراخوانی `Base.metadata.create_all(bind=engine)` تمامی جداول را بر اساس مدل‌های تعریف‌شده ایجاد کرده است.
   - این فراخوانی معمولاً در شروع برنامه (مثلاً در `main.py`) انجام شده است.

5. **مدیریت نشست (Session) با Dependency Injection:**
   - تابع `get_session()` به‌عنوان وابستگی (Dependency) در FastAPI تعریف شده است.
   - در هر درخواست، یک session جدید باز شده، پس از انجام عملیات commit می‌شود و در صورت خطا rollback صورت می‌گیرد.
   - نوع `SessionDep` برای تزریق آسان session در endpointها استفاده شده است.

**مزایای رویکرد انتخابی:**
- **قدرت و انعطاف SQLAlchemy** در تعریف روابط پیچیده و کوئری‌های پیشرفته
- **پشتیبانی داخلی از Migration** (هرچند در این پروژه از Alembic استفاده نشده)
- **مدیریت خودکار تراکنش‌ها** با استفاده از session و dependency injection
- **بهینه‌سازی برای محیط وب** با فعال‌سازی WAL و افزایش timeout

**خروجی نهایی:**
- یک فایل `database.db` شامل تمام جداول با رعایت یکپارچگی کلیدهای خارجی
- مدل‌های SQLAlchemy آماده برای استفاده در endpointهای FastAPI
- سیستم مدیریت session ایمن و خودکار برای هر درخواست
 نموداردیاگرام: <img width="990" height="1318" alt="database db 2" src="https://github.com/user-attachments/assets/fd7aa919-83d2-4f51-8fc1-1999161c0cd5" />

---


**گزارش مرحله ۵ – پیاده‌سازی عملیات پایگاه داده در قالب وب‌سرویس با معماری سه‌لایه**

**معماری انتخابی:**  
پروژه با **معماری سه‌لایه (Three-Layer Architecture)** سازماندهی شده است که شامل لایه‌های زیر می‌باشد:

1. **لایه Presentation (Routers/Endpoint)**  
2. **لایه Business schemas (Service)**  
3. **لایه Data Access (Model/Repository)**  

**ساختار پوشه‌ها :**
```
PythonProject21/
├── .venv/                    # محیط مجازی پایتون
├── app/                      # پوشه اصلی اپلیکیشن
│   ├── models/              # مدل‌های دیتابیس (SQLAlchemy)
│   ├── routers/             # endpointهای FastAPI (روترها)
│   ├── schemas/             # مدل‌های Pydantic (Request/Response)
│   ├── __init__.py          # شناسایی پوشه به عنوان پکیج
│   ├── config.py            # تنظیمات کلی برنامه
│   └── db.py                # تنظیمات اتصال به پایگاه داده
├── nginx/                   # پیکربندی Nginx (برای مرحله‌های بعدی)
├── app_database.db          # فایل پایگاه داده SQLite (ممکن است نمونه قدیمی باشد)
├── database.db              # فایل اصلی پایگاه داده SQLite
├── docker-compose.yml       # تنظیمات Docker Compose
├── Dockerfile               # تعریف image داکر
├── main.py                  # نقطه ورود اصلی برنامه
├── requirements.txt         # وابستگی‌های پایتون
├── security.py              # ماژول امنیتی (مثلاً برای احراز هویت)
├── test_db.py               # تست‌های پایگاه داده
└── README.md                # مستندات پروژه
```

---

**گام‌های انجام شده برای هر موجودیت (مثال: Farmer):**

### **۱. لایه Data Access (مدل‌های دیتابیس)**
- فایل: `app/models/farmer_model.py`
- تعریف مدل SQLAlchemy با فیلدها و روابط مربوطه
- مثال:
  ```python
  from sqlalchemy import Column, Integer, String
  from sqlalchemy.orm import relationship
  from app.db import Base

  class FarmerModel(Base):
      __tablename__ = "farmers"
      id = Column(Integer, primary_key=True, index=True)
      name = Column(String)
      phone = Column(String)
      # روابط با دیگر جداول
      contracts = relationship("ContractModel", back_populates="farmer")
  ```

### **۲. لایه Schema (مدل‌های Pydantic)**
- فایل: `app/schemas/farmer_schema.py`
- تعریف ساختار داده برای ورودی و خروجی API
- مثال:
  ```python
  from pydantic import BaseModel
  from typing import List, Optional

  class FarmerBase(BaseModel):
      name: str
      phone: str

  class FarmerCreate(FarmerBase):
      pass

  class FarmerResponse(FarmerBase):
      id: int
      class Config:
          orm_mode = True
  ```

### **۳. لایه Business Logic (سرویس)**
- **توجه:** بر اساس ساختار شما، ممکن است سرویس‌ها در خود روترها یا در پوشه‌ای جداگانه پیاده‌سازی شده باشند.
- اگر پوشه `services/` دارید، مثال:
  ```python
  # app/services/farmer_service.py
  from sqlalchemy.orm import Session
  from app.models.farmer_model import FarmerModel
  from app.schemas.farmer_schema import FarmerCreate

  class FarmerService:
      def create_farmer(self, db: Session, farmer_data: FarmerCreate):
          farmer = FarmerModel(**farmer_data.dict())
          db.add(farmer)
          db.commit()
          db.refresh(farmer)
          return farmer
  ```

### **۴. لایه Presentation (روتر)**
- فایل: `app/routers/farmer_router.py`
- تعریف endpointهای FastAPI با استفاده از `APIRouter`
- مثال:
  ```python
  from fastapi import APIRouter, Depends, HTTPException
  from sqlalchemy.orm import Session
  from app.schemas.farmer_schema import FarmerCreate, FarmerResponse
  from app.db import get_session
  from app.models.farmer_model import FarmerModel

  router = APIRouter(prefix="/farmers", tags=["Farmers"])

  @router.post("/", response_model=FarmerResponse)
  def create_farmer(farmer: FarmerCreate, db: Session = Depends(get_session)):
      db_farmer = FarmerModel(**farmer.dict())
      db.add(db_farmer)
      db.commit()
      db.refresh(db_farmer)
      return db_farmer
  ```

### **۵. یکپارچه‌سازی در main.py**
- در `main.py` تمام روترها import و به برنامه FastAPI اضافه شده‌اند:
  ```python
  from fastapi import FastAPI
  from app.routers import farmer, product, contract, ...  # import روترها
  from app.db import create_db_and_tables

  app = FastAPI(title="HavirKesht API", version="1.0.0")

  # ایجاد جداول در شروع برنامه
  @app.on_event("startup")
  def on_startup():
      create_db_and_tables()

  # ثبت روترها
  app.include_router(farmer.router)
  app.include_router(product.router)
  app.include_router(contract.router)
  ```

---

**مزایای معماری استفاده‌شده:**
- **جدا شدن نگرانی‌ها:** تغییر در منطق کسب‌وکار تأثیری روی لایه presentation ندارد.
- **قابلیت تست‌پذیری:** هر لایه به‌طور مستقل قابل unit testing است.
- **قابلیت نگهداری:** افزودن endpointهای جدید با کپی‌کردن ساختار موجود آسان است.
- **مستندسازی خودکار:** FastAPI به‌طور خودکار مستندات Swagger در `/docs` ایجاد می‌کند.

---

**خروجی نهایی مرحله ۵:**
- ✅ مجموعه کاملی از APIهای RESTful برای مدیریت موجودیت‌های اصلی پروژه (کشاورز، محصول، قرارداد، تراکنش و...)
- ✅ مستندسازی خودکار APIها در مسیر `/docs`
- ✅ پوشه‌بندی منظم و قابل توسعه
- ✅ آماده‌سازی برای مراحل بعدی (Docker، Nginx، CI/CD)

---

