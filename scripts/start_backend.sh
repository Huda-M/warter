@echo off
echo 🚀 بدء تشغيل خادم التوأم الرقمي...

cd backend

REM التحقق من وجود بيئة virtual
if not exist "venv" (
    echo 🔧 إنشاء بيئة افتراضية...
    python -m venv venv
)

REM تفعيل البيئة
call venv\Scripts\activate.bat

REM تثبيت المتطلبات
echo 📦 تثبيت المتطلبات...
pip install -r requirements.txt

REM تشغيل الخادم
echo 🌐 تشغيل الخادم على http://localhost:5000
python app.py