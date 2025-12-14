@echo off
echo 🎨 بدء تشغيل واجهة التوأم الرقمي...

cd frontend

REM تثبيت المتطلبات
if not exist "node_modules" (
    echo 📦 تثبيت المتطلبات...
    npm install
)

REM تشغيل التطبيق
echo 🌐 تشغيل التطبيق على http://localhost:3000
npm start