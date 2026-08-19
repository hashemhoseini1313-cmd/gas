[app]
# نسخهی پایتون برای اندروید (مهم)
android.python_version = 3.10

# مشخصات برنامه
title = Screen Recorder
package.name = screenrecorder
package.domain = org.example

source.dir = .
source.include_exts = py,java,png,jpg,kv,ttf

version = 1.0

# نیازمندیها
# (pyjnius خودکار همراه Kivy هست؛ اگر خطا گرفتی میتونی اضافه کنی)
requirements = python3,kivy==2.2.1,arabic_reshaper

# جهت و حالت نمایش
orientation = portrait
fullscreen = 0

# تنظیمات اندروید 15 (API 34 یا 35)
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# مجوزهای لازم برای ضبط صفحه، عکس و ذخیرهسازی
android.permissions = INTERNET,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PROJECTION,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# اضافه کردن فایلهای Java و Manifest سفارشی
android.add_src = src
android.add_manifest = manifest.xml
android.services = ScreenCaptureService:org.example.screenrecorder.ScreenCaptureService

# پذیرش لایسنس SDK
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
