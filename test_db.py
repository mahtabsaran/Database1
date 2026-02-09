# test_db.py
from app.db import engine, SessionLocal
from sqlalchemy import text


def test_database_connection():
    """تست اتصال به پایگاه داده"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ اتصال به پایگاه داده موفقیت‌آمیز بود")
            return True
    except Exception as e:
        print(f"❌ خطا در اتصال به پایگاه داده: {e}")
        return False


def test_tables_exist():
    """تست وجود جداول"""
    try:
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)).fetchall()

            print(f"✅ تعداد جداول ایجاد شده: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
            return True
    except Exception as e:
        print(f"❌ خطا در بررسی جداول: {e}")
        return False


if __name__ == "__main__":
    print("🔍 شروع تست پایگاه داده...")
    test_database_connection()
    test_tables_exist()