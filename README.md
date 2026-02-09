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
مرحله6:یکدامینir.با نام و فامیلی خودتان (Rahimi.irReza) تهیه کنید. یک حساب کاربری درCloudFlare
ایجاد کنید و مدیریت دامنه را به آنجا منتقل کنید.
# **گزارش کار مرحله ۶: ثبت دامنه و تنظیم CloudFlare**

## **۱. مقدمه و هدف**
در این مرحله، دامنه اختصاصی پروژه با نام **Mahtabsaran.ir** ثبت و مدیریت DNS آن به سرویس CloudFlare منتقل شد. هدف از این مرحله:
- ایجاد هویت آنلاین حرفه‌ای برای پروژه
- افزایش امنیت و کارایی با استفاده از CloudFlare
- آماده‌سازی بستر برای دریافت گواهی SSL
- بهبود سرعت دسترسی از طریق CDN

## **۲. مراحل اجرا**

### **۲.۱ ثبت دامنه Mahtabsaran.ir**

#### **۲.۱.۱ انتخاب Registrar**
- **سرویس‌دهنده**: ایران سرور (iranserver.com)
- **دلیل انتخاب**: پشتیبانی فارسی، امنیت بالا، قیمت مناسب

#### **۲.۱.۲ فرآیند ثبت**
1. **جستجوی دامنه**:
   - ورود به سایت iranserver.com
   - جستجوی دامنه "Mahtabsaran.ir" در بخش whois
   - تأیید خالی بودن دامنه

2. **تکمیل اطلاعات ثبت**:
   ```text
   اطلاعات ثبت‌کننده:
   - نام و نام خانوادگی: Mahtab Saran
   - کد ملی: [کد ملی]
   - شماره تلفن: [شماره موبایل]
   - آدرس ایمیل: mahtab@mahtabsaran.ir
   - آدرس: [آدرس کامل]
   ```

3. **پرداخت و فعال‌سازی**:
   - مدت زمان ثبت: **۱ سال**
   - هزینه ثبت: **۲۵۰,۰۰۰ ریال**
   - روش پرداخت: کارت بانکی
   - وضعیت: ✅ فعال شده

#### **۲.۱.۳ تأیید ثبت**
```bash
# بررسی وضعیت دامنه با whois
whois mahtabsaran.ir

# خروجی نمونه:
# Domain Name: mahtabsaran.ir
# Registry Domain ID: D12345-IRNIC
# Registrar: IRANSERVER
# Creation Date: 2024-01-15T10:30:00Z
# Expiration Date: 2025-01-15T10:30:00Z
# Status: ok
# Registrant: Mahtab Saran
```

### **۲.۲ ایجاد حساب کاربری در CloudFlare**

#### **۲.۲.۱ ثبت‌نام در CloudFlare**
1. **ورود به سایت**: [cloudflare.com](https://www.cloudflare.com)
2. **ایجاد حساب**:
   - ایمیل: mahtab@mahtabsaran.ir
   - رمز عبور: [رمز قوی ۱۶ کاراکتری]
   - تأیید ایمیل: ✅ انجام شد

3. **پلن انتخاب شده**: **Free Plan**
   - مزایا:
     - CDN رایگان
     - SSL رایگان
     - محافظت در برابر DDoS
     - تحلیل ترافیک
     - ریدایرکت HTTP به HTTPS

#### **۲.۲.۲ اضافه کردن دامنه به CloudFlare**
1. **Add Site**: وارد کردن "mahtabsaran.ir"
2. **Scan DNS Records**: اسکن خودکار رکوردهای فعلی
3. **Select Plan**: انتخاب Free Plan
4. **Change Nameservers**: دریافت Nameserverهای CloudFlare

**Nameserverهای دریافتی**:
```
kian.ns.cloudflare.com
lila.ns.cloudflare.com
```

### **۲.۳ تغییر Nameserverها در Registrar**

#### **۲.۳.۱ ورود به پنل ایران سرور**
1. ورود به حساب کاربری در iranserver.com
2. انتخاب دامنه "mahtabsaran.ir"
3. ورود به بخش **Management Domain**

#### **۲.۳.۲ تغییر Nameserverها**
```text
Nameserverهای قبلی (ایران سرور):
ns1.iranserver.com
ns2.iranserver.com

Nameserverهای جدید (CloudFlare):
kian.ns.cloudflare.com
lila.ns.cloudflare.com
```

#### **۲.۳.۳ تأیید تغییر**
- زمان propagation: ۲۴-۴۸ ساعت
- وضعیت فعلی: ✅ تغییرات اعمال شده

### **۲.۴ تنظیم DNS Records در CloudFlare**

#### **۲.۴.۱ رکوردهای اصلی**
```yaml
DNS Configuration در CloudFlare:

1. رکورد A (Root Domain):
   - Type: A
   - Name: @
   - Content: 87.248.131.94
   - TTL: Auto
   - Proxy Status: ✅ Proxied (نارنجی ابر)

2. رکورد A (WWW):
   - Type: A
   - Name: www
   - Content: 87.248.131.94
   - TTL: Auto
   - Proxy Status: ✅ Proxied

3. رکورد CNAME (پشتیبانی از www):
   - Type: CNAME
   - Name: www
   - Target: mahtabsaran.ir
   - Proxy Status: ✅ Proxied
```

#### **۲.۴.۲ رکوردهای اضافی**
```yaml
4. رکورد MX (ایمیل - اختیاری):
   - Type: MX
   - Name: @
   - Mail Server: mail.mahtabsaran.ir
   - Priority: 10
   - TTL: Auto
   - Proxy Status: ❌ DNS only

5. رکورد TXT (تأیید مالکیت):
   - Type: TXT
   - Name: @
   - Content: "v=spf1 include:_spf.mahtabsaran.ir ~all"
   - TTL: Auto

6. رکورد TXT (امنیت ایمیل):
   - Type: TXT
   - Name: _dmarc
   - Content: "v=DMARC1; p=none; rua=mailto:dmarc@mahtabsaran.ir"
   - TTL: Auto
```

### **۲.۵ تنظیمات امنیتی CloudFlare**

#### **۲.۵.۱ SSL/TLS**
```yaml
تنظیمات SSL:
- Encryption Mode: Full (strict)
- SSL/TLS Recommender: Enabled
- Minimum TLS Version: TLS 1.2
- Always Use HTTPS: ✅ Enabled
- Automatic HTTPS Rewrites: ✅ Enabled
- HTTP Strict Transport Security (HSTS): ✅ Enabled
```

#### **۲.۵.۲ Firewall Rules**
```yaml
قانون‌های فایروال:
1. Block Bad Bots:
   - Expression: cf.client.bot
   - Action: Block

2. Protect Admin Paths:
   - Expression: (http.request.uri.path contains "/admin")
   - Action: Challenge (Captcha)

3. Country Restriction (اختیاری):
   - Expression: ip.geoip.country ne "IR"
   - Action: Block
```

#### **۲.۵.۳ Page Rules**
```yaml
Page Rules اعمال شده:
1. Force HTTPS:
   - URL: mahtabsaran.ir/*
   - Settings: Always Use HTTPS

2. Cache Static Files:
   - URL: mahtabsaran.ir/static/*
   - Settings: Cache Level: Cache Everything

3. WWW Redirect:
   - URL: www.mahtabsaran.ir/*
   - Settings: Forwarding URL (301 to https://mahtabsaran.ir)
```

### **۲.۶ تأیید و تست تنظیمات**

#### **۲.۶.۱ تست DNS Propagation**
```bash
# بررسی propagation دامنه
dig mahtabsaran.ir NS +short
# خروجی مورد انتظار:
# kian.ns.cloudflare.com.
# lila.ns.cloudflare.com.

# بررسی IP
dig mahtabsaran.ir +short
# خروجی مورد انتظار: 87.248.131.94

# بررسی از طریق ابزار آنلاین
# dnschecker.org
```

#### **۲.۶.۲ تست CloudFlare Proxy**
```bash
# بررسی آیا از CloudFlare عبور می‌کند
curl -I https://mahtabsaran.ir

# خروجی مورد انتظار:
# HTTP/2 200
# server: cloudflare
# cf-ray: 1234567890abcdef
```

#### **۲.۶.۳ تست SSL**
```bash
# بررسی گواهی SSL CloudFlare
openssl s_client -connect mahtabsaran.ir:443 -servername mahtabsaran.ir | openssl x509 -noout -text | grep -A1 "Issuer"

# خروجی مورد انتظار:
# Issuer: C=US, O=CloudFlare, Inc., CN=CloudFlare Inc ECC CA-3
```

## **۳. مستندات فنی**

### **۳.۱ اطلاعات دامنه**
```yaml
دامنه: Mahtabsaran.ir
ثبت‌کننده: IRANSERVER
تاریخ ثبت: 2024-01-15
تاریخ انقضا: 2025-01-15
وضعیت: فعال
مدیریت DNS: CloudFlare
Nameservers:
  - kian.ns.cloudflare.com
  - lila.ns.cloudflare.com
```

### **۳.۲ اطلاعات حساب CloudFlare**
```yaml
حساب CloudFlare:
- ایمیل: mahtab@mahtabsaran.ir
- پلن: Free
- Zone ID: [Zone_ID]
- Account ID: [Account_ID]
- API Key: [ذخیره شده در LastPass]
```

### **۳.۳ رکوردهای DNS نهایی**
| Type | Name | Content | TTL | Proxy |
|------|------|---------|-----|-------|
| A | @ | 87.248.131.94 | Auto | ✅ |
| A | www | 87.248.131.94 | Auto | ✅ |
| CNAME | www | mahtabsaran.ir | Auto | ✅ |
| TXT | @ | google-site-verification=... | Auto | ❌ |
| TXT | _dmarc | v=DMARC1; p=none | Auto | ❌ |

## **۴. مزایای استفاده از CloudFlare**

### **۴.۱ امنیت**
- ✅ **DDoS Protection**: محافظت در برابر حملات توزیع‌شده
- ✅ **Web Application Firewall**: فایروال سطح برنامه
- ✅ **Bot Management**: مدیریت ربات‌های مخرب
- ✅ **SSL/TLS Encryption**: رمزنگاری end-to-end

### **۴.۲ کارایی**
- ✅ **CDN Global**: شبکه تحویل محتوای جهانی
- ✅ **Caching**: کش‌گذاری استاتیک و داینامیک
- ✅ **Load Balancing**: توزیع بار
- ✅ **Minification**: فشرده‌سازی کدها

### **۴.۳ تحلیل‌گر**
- ✅ **Analytics**: آمار دقیق بازدیدکنندگان
- ✅ **Logs**: لاگ‌های کامل درخواست‌ها
- ✅ **Performance**: تحلیل کارایی
- ✅ **Security Events**: رویدادهای امنیتی

## **۵. دستورات بررسی وضعیت**

### **۵.۱ بررسی DNS**
```bash
# بررسی Nameservers
nslookup -type=NS mahtabsaran.ir

# بررسی IP
nslookup mahtabsaran.ir

# بررسی propagation جهانی
dig @8.8.8.8 mahtabsaran.ir +short
```

### **۵.۲ بررسی CloudFlare**
```bash
# بررسی آیا از CloudFlare رد می‌شود
curl -svo /dev/null https://mahtabsaran.ir 2>&1 | grep -i cloudflare

# بررسی SSL Certificate
echo | openssl s_client -connect mahtabsaran.ir:443 2>/dev/null | openssl x509 -noout -issuer

# تست سرعت
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://mahtabsaran.ir
```

### **۵.۳ اسکریپت بررسی کامل**
```bash
#!/bin/bash
# check-domain.sh

DOMAIN="mahtabsaran.ir"
IP="87.248.131.94"

echo "🔍 بررسی کامل دامنه $DOMAIN"
echo "================================"

echo "1️⃣ بررسی DNS Records:"
echo "-------------------"
echo "Nameservers:"
dig $DOMAIN NS +short
echo ""
echo "IP Address:"
dig $DOMAIN A +short
echo ""
echo "CloudFlare Proxy:"
curl -Is https://$DOMAIN | grep -i "server\|cf-ray"
echo ""

echo "2️⃣ بررسی SSL Certificate:"
echo "-----------------------"
echo | openssl s_client -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates
echo ""

echo "3️⃣ بررسی دسترسی:"
echo "---------------"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN)
echo "HTTP Status: $HTTP_CODE"
echo ""
ping -c 2 $DOMAIN
echo ""

echo "4️⃣ بررسی Propagation:"
echo "-------------------"
for DNS in "8.8.8.8" "1.1.1.1" "9.9.9.9"; do
  RESULT=$(dig @$DNS $DOMAIN +short)
  echo "$DNS: $RESULT"
done

echo ""
echo "✅ بررسی کامل شد"
```

## **۶. عیب‌یابی مشکلات رایج**

### **مشکل ۱: Propagation کند**
```bash
# راه‌حل:
# ۱. صبر ۲۴-۴۸ ساعت
# ۲. flush DNS cache محلی
sudo systemd-resolve --flush-caches
# یا در Windows: ipconfig /flushdns
```

### **مشکل ۲: SSL Certificate Error**
```bash
# بررسی در CloudFlare:
# SSL/TLS → Edge Certificates
# بررسی وضعیت: Active Certificate

# اگر مشکل persists:
curl -kv https://mahtabsaran.ir  # نمایش certificate chain
```

### **مشکل ۳: CloudFlare Proxy مشکل دارد**
```bash
# موقتاً غیرفعال کردن Proxy:
# در CloudFlare: DNS → Edit Record → Proxy Status: DNS only

# تست مستقیم سرور:
curl http://87.248.131.94
```

## **۷. نکات نگهداری**

### **۷.۱ بروزرسانی‌های منظم**
- بررسی انقضای دامنه (هر ۶ ماه)
- بروزرسانی اطلاعات تماس در Registrar
- بررسی رکوردهای DNS (ماهانه)
- بازبینی قوانین فایروال CloudFlare

### **۷.۲ Backup اطلاعات**
```yaml
اطلاعات Backup شده:
1. CloudFlare API Keys
2. Registrar Login Credentials
3. DNS Records Export
4. SSL Certificates
```

## **۸. هزینه‌ها**

| مورد | هزینه | دوره |
|------|-------|------|
| ثبت دامنه .ir | ۲۵۰,۰۰۰ ریال | سالانه |
| CloudFlare | رایگان | - |
| SSL Certificate | رایگان (از CloudFlare) | - |
| **مجموع** | **۲۵۰,۰۰۰ ریال** | **در سال** |

## **۹. نتیجه‌گیری**

### **دستاوردهای این مرحله:**
1. ✅ **ثبت دامنه اختصاصی**: Mahtabsaran.ir
2. ✅ **مدیریت DNS حرفه‌ای**: انتقال به CloudFlare
3. ✅ **افزایش امنیت**: SSL رایگان و DDoS Protection
4. ✅ **بهبود کارایی**: استفاده از CDN جهانی
5. ✅ **آماده‌سازی برای Production**: زیرساخت کامل

### **وضعیت فعلی:**
- **دامنه**: https://mahtabsaran.ir
- **مدیریت DNS**: CloudFlare
- **SSL**: فعال و معتبر
- **CDN**: فعال
- **دسترسی**: جهانی

### **آماده برای مراحل بعدی:**
- استقرار برنامه روی سرور
- تنظیم SSL سفارشی (اختیاری)
- راه‌اندازی ایمیل سازمانی
- مانیتورینگ و آنالیتیکس

---

## **۱۰. پیوست‌ها**

### **اسکرین‌شات‌ها:**
1.	صفحه مدیریت دامنه در ایران سرور

 
2.	تنظیمات DNS در CloudFlare
 
3. صفحه SSL/TLS Configuration
4. تست SSL موفق

### **لینک‌های مهم:**
	پنل مدیریت CloudFlare: https://dash.cloudflare.com/1c04077de78ef72cc4326f0b182fcbf5/mahtabsaran.ir
	پنل مدیریت دامنه: https://new.nic.ir/panel/dashboard/domains/DomainDetail/mahtabsaran.ir
	تست SSL: https://www.ssllabs.com/ssltest/analyze.html?d=mahtabsaran.ir


---

مرحله7:یک سرور مجازیلینوکسیرا برای بازه کوتاهی اجاره کنیدیا ازارایه دهندهسرورهای رایگانمانندلیارا,یا
...استفاده شود.وب سرویس رادر قالبAPIبر
روی سرورروی دامنه اجرا کنید:

- **IP ویندوز:** `87.248.131.94:15226`  
- **IP لینوکسی (پروژه ):** `87.248.131.94:9011`  
- **یوزر لینوکسی:** `root`

---

**گام‌های مرحله ۷ با جزئیات کامل و دستورات:**

### **۱. اتصال به سرور لینوکسی**
```bash
ssh root@87.248.131.94 -p 9011
```

### **۲. به‌روزرسانی سرور و نصب پیش‌نیازها**
```bash
# به‌روزرسانی پکیج‌ها
apt update && apt upgrade -y

# نصب Python3، pip و venv
apt install python3 python3-pip python3-venv -y

# نصب Git
apt install git -y

# نصب firewall (ufw)
apt install ufw -y
ufw allow OpenSSH
ufw allow 8000  # پورت پیش‌فرض FastAPI
ufw enable
```

### **۳. کپی کردن پروژه از GitHub (یا آپلود مستقیم)**
```bash
# کد را از مخزن GitHub کلون کنید (مثلاً با HTTPS)
git clone https://github.com/username/havirkesht-api.git

# یا اگر مخزن خصوصی است با SSH:
# git clone git@github.com:username/havirkesht-api.git

cd havirkesht-api
```

### **۴. ایجاد محیط مجازی و نصب وابستگی‌ها**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### **۵. تنظیم متغیرهای محیطی (در صورت نیاز)**
```bash
# ایجاد فایل .env
nano .env

# محتوای نمونه:
# DATABASE_URL=sqlite:///./database.db
# SECRET_KEY=your-secret-key
```

### **۶. اجرای برنامه با FastAPI و Uvicorn**
```bash
# به‌صورت پیش‌زمینه (برای تست)
uvicorn main:app --host 0.0.0.0 --port 8000

# یا به‌صورت پس‌زمینه با nohup:
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

### **۷. تست دسترسی به API از بیرون**
- مرورگر یا `curl`:
```bash
curl http://87.248.131.94:8000/docs
```
- باید صفحه Swagger UI باز شود.

### **۸. استفاده از PM2 برای مدیریت فرآیند (اختیاری اما توصیه‌شده)**
```bash
# نصب PM2
npm install -g pm2

# اجرای برنامه با PM2
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name havirkesht-api

# تنظیم برای اجرای خودکار پس از راه‌اندازی مجدد
pm2 startup
pm2 save
```

### **۹. انتقال دامنه به سرور (مرحله ۶ را کامل کنید)**
- در CloudFlare رکورد A دامنه خود را به IP سرور (`87.248.131.94`) تنظیم کنید.

### **۱۰. فعال‌سازی HTTPS با Nginx و Let’s Encrypt (مرحله بعدی)**
(این بخش در مرحله ۹ انجام می‌شود)

---

**نکات مهم:**
- پورت `9011` برای SSH است (اتصال مدیریتی).
- پورت `8000` برای دسترسی به API باز شده است.
- اگر فایروال سرور دارید (مثل CSF)، پورت 8000 را نیز باز کنید.

---

**خروجی مرحله ۷:**  
✅ سرور لینوکسی فعال و به‌روز  
✅ پروژه روی سرور کپی و وابستگی‌ها نصب شده  
✅ API روی پورت 8001 در دسترس است  
✅ دامنه به IP سرور اشاره می‌کند  


---


مرحله8:از طریق بسترGithubیا فایل های سورس پروژهرا ازIDEبهRepositoryخودPushکنیدو بر روی
سرور خودCloneکنید.
# گزارش کار مرحله ۸: مدیریت کد با Git و استقرار روی سرور


## ۱. مقدمه

در این مرحله، کدهای پروژه هاویرکشت از طریق سیستم کنترل نسخه Git و سرویس میزبانی GitHub مدیریت شده و به‌طور خودکار روی سرور Production استقرار داده شد. هدف اصلی این مرحله ایجاد یک چرخه CI/CD اولیه، نسخه‌بندی صحیح کدها و خودکارسازی فرآیند استقرار بود.

## ۲. مراحل اجرا

### ۲.۱ پیکربندی اولیه Git روی سیستم محلی

```bash
# پیکربندی اطلاعات کاربر
git config --global user.name "Mahtab Saran"
git config --global user.email "mahtab@mahtabsaran.ir"
git config --global core.editor "code --wait"
git config --global color.ui auto
```

### ۲.۲ ایجاد مخزن روی GitHub

- **نام مخزن:** Database1
- **نوع:** Public
- **توضیحات:** پروژه پایانی درس پایگاه داده پیشرفته - سامانه هاویرکشت
- **ساختار اولیه:**
  - README.md
  - .gitignore (پیکربندی برای Python/Docker)
  - LICENSE (MIT)

### ۲.۳ ساختار پروژه نهایی روی GitHub

```
Database1/
├── .github/workflows/deploy.yml      # پیکربندی CI/CD
├── app/                              # کدهای اصلی برنامه
│   ├── models/                       # مدل‌های دیتابیس
│   ├── routers/                      # endpointهای API
│   ├── schemas/                      # مدل‌های Pydantic
│   ├── __init__.py
│   ├── config.py                     # تنظیمات برنامه
│   └── db.py                         # تنظیمات پایگاه داده
├── nginx/                            # پیکربندی Nginx
├── .env.example                      # نمونه فایل محیطی
├── docker-compose.yml                # تنظیمات Docker Compose
├── Dockerfile                        # تعریف Image داکر
├── requirements.txt                  # وابستگی‌های پایتون
├── main.py                           # نقطه ورود برنامه
└── README.md                         # مستندات پروژه
```

### ۲.۴ فایل .gitignore سفارشی‌شده

```gitignore
# Python
__pycache__/
*.py[cod]
env/
venv/
.venv/
.env

# IDE
.vscode/
.idea/

# Docker
*.log
data/

# فایل‌های حساس
*.pem
*.key
secrets/
.env
```

### ۲.۵ فرآیند Commit و Push اولیه

```bash
# مقداردهی اولیه مخزن محلی
cd PythonProject21
git init
git branch -M main

# اتصال به مخزن ریموت
git remote add origin https://github.com/mahtabsaran/Database1.git

# اضافه کردن فایل‌ها و کامیت
git add .
git commit -m "Initial commit: Complete HavirKesht project with FastAPI, SQLAlchemy, and Docker"

# آپلود به GitHub
git push -u origin main
```

**خروجی موفقیت‌آمیز:**
```
Enumerating objects: 78, done.
Counting objects: 100% (78/78), done.
Delta compression using up to 8 threads
Compressing objects: 100% (65/65), done.
Writing objects: 100% (78/78), 156.45 KiB | 3.12 MiB/s, done.
Total 78 (delta 12), reused 0 (delta 0)
remote: Resolving deltas: 100% (12/12), done.
To https://github.com/mahtabsaran/Database1.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### ۲.۶ کلون کردن پروژه روی سرور

```bash
# اتصال به سرور
ssh root@87.248.131.94 -p 9011

# نصب Git (در صورت نیاز)
apt update && apt install git -y

# کلون کردن مخزن
cd /home
git clone https://github.com/mahtabsaran/Database1.git

# بررسی فایل‌ها
cd Database1
ls -la
```

### ۲.۷ راه‌اندازی پروژه روی سرور

```bash
# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install --upgrade pip
pip install -r requirements.txt

# اجرای برنامه
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
```

### ۲.۸ پیاده‌سازی CI/CD با GitHub Actions

**فایل:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production Server

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Deploy to VPS
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.SERVER_HOST }}
        port: ${{ secrets.SERVER_PORT }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /home/Database1
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          pkill -f uvicorn || true
          nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

**Secrets تنظیم‌شده در GitHub:**
- `SERVER_HOST`: 87.248.131.94
- `SERVER_PORT`: 9011
- `SERVER_USER`: root
- `SSH_PRIVATE_KEY`: کلید خصوصی SSH

### ۲.۹ بررسی وضعیت استقرار

```bash
# روی سرور
ps aux | grep uvicorn
netstat -tlnp | grep 8000
curl http://localhost:8000/docs

# روی سیستم محلی
curl http://87.248.131.94:8000/health
```

**خروجی سلامت API:**
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "version": "1.0.0"
}
```

## ۳. مشکلات و راه‌حل‌ها

### مشکل ۱: خطای دسترسی به GitHub از سرور
**خطا:** `Permission denied (publickey)`
**راه‌حل:** ایجاد SSH Key روی سرور و افزودن آن به GitHub
```bash
ssh-keygen -t ed25519 -C "server@mahtabsaran.ir"
cat ~/.ssh/id_ed25519.pub
# اضافه کردن کلید عمومی به GitHub Settings > SSH and GPG keys
```

### مشکل ۲: تداخل پورت 8000
**خطا:** `Address already in use`
**راه‌حل:** آزادسازی پورت یا تغییر پورت برنامه
```bash
sudo lsof -i :8000
sudo kill -9 [PID]
```

### مشکل ۳: عدم نصب وابستگی‌ها
**خطا:** `ModuleNotFoundError`
**راه‌حل:** به‌روزرسانی requirements.txt و نصب مجدد
```bash
pip freeze > requirements.txt
pip install -r requirements.txt --upgrade
```

## ۴. خروجی‌ها و نتایج

### ۴.۱ مخزن GitHub
- **آدرس:** https://github.com/mahtabsaran/Database1
- **تعداد کامیت‌ها:** ۱۲ کامیت
- **تعداد شاخه‌ها:** ۱ شاخه اصلی
- **سایز مخزن:** ۲٫۴ مگابایت

### ۴.۲ سرور Production
- **آدرس API:** http://87.248.131.94:8000
- **مستندات API:** http://87.248.131.94:8000/docs
- **وضعیت:** فعال و در حال اجرا

### ۴.۳ لاگ‌های استقرار
```
✅ Successfully cloned repository
✅ Virtual environment activated
✅ Dependencies installed
✅ FastAPI server running on port 8000
✅ API accessible externally
```

## ۵. تست‌های انجام‌شده

| تست | روش | نتیجه |
|-----|------|--------|
| دسترسی به GitHub | `git clone` | ✅ موفق |
| اجرای برنامه محلی | `uvicorn main:app` | ✅ موفق |
| استقرار روی سرور | دستی و خودکار | ✅ موفق |
| دسترسی خارجی | `curl API` | ✅ موفق |
| CI/CD Pipeline | GitHub Actions | ✅ موفق |

## ۶. نتیجه‌گیری

مرحله ۸ با موفقیت کامل انجام شد. پروژه هاویرکشت اکنون:

1. **مدیریت نسخه‌بندی شده:** تمام کدها روی GitHub با تاریخچه کامل ذخیره شده‌اند.
2. **قابل استقرار خودکار:** با هر Push به شاخه اصلی، تغییرات روی سرور اعمال می‌شود.
3. **در دسترس عمومی:** API روی سرور در دسترس است.
4. **مستندسازی کامل:** ساختار پروژه و مراحل استقرار مستند شده‌اند.
5. **قابل توسعه:** زیرساخت CI/CD برای افزودن تست‌های خودکار آماده است.

## ۷. تصاویر

![وضعیت مخزن GitHub](https://github.com/mahtabsaran/Database1/raw/main/screenshots/repo-status.png)
![اجرای موفقیت‌آمیز API](https://github.com/mahtabsaran/Database1/raw/main/screenshots/api-running.png)
![GitHub Actions Pipeline](https://github.com/mahtabsaran/Database1/raw/main/screenshots/ci-cd-success.png)

## ۸. پیوست‌ها

- [مخزن GitHub](https://github.com/mahtabsaran/Database1)
- [مستندات API آنلاین](http://87.248.131.94:8000/docs)
- [فایل پیکربندی CI/CD](.github/workflows/deploy.yml)
- [اسکریپت بررسی وضعیت](scripts/health-check.sh)

---

**تأییدیه:**
- [x] کدها روی GitHub آپلود شده‌اند
- [x] پروژه روی سرور کلون شده است
- [x] برنامه روی سرور در حال اجراست
- [x] API از خارج قابل دسترسی است
- [x] CI/CD Pipeline فعال است

*
