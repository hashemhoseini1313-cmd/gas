[app]
p4a.branch = 2024.1.21
# مشخصات برنامه
title = Screen Recorder
package.name = screenrecorder
package.domain = org.example

source.dir = .
source.include_exts = py,java,png,jpg,kv,ttf,otf

version = 1.0

# نیازمندی‌ها (تعیین دقیق نسخه پایتون برای جلوگیری از دانلود پایتون 3.14)
requirements = python3==3.10.12,hostpython3==3.10.12,kivy,arabic_reshaper,python-bidi

# جهت و حالت نمایش
orientation = portrait
fullscreen = 0

# تنظیمات اندروید 14 و 15
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# مجوزهای لازم برای ضبط صفحه، صدا، عکس و ذخیره‌سازی در اندروید 14/15
android.permissions = INTERNET,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PROJECTION,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,POST_NOTIFICATIONS

# اضافه کردن فایل‌های Java و Manifest سفارشی شما
android.add_src = src
android.manifest_path = manifest.xml
android.services = ScreenCaptureService:org.example.screenrecorder.ScreenCaptureService

# پذیرش لایسنس SDK
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
