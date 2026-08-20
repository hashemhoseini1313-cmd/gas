[app]
title = Screen Recorder
package.name = screenrecorder
package.domain = org.example

source.dir = .
source.include_exts = py,java,png,jpg,kv,ttf,otf

version = 1.0

# نیازمندی‌ها (نسخهٔ یکسان پایتون)
requirements = python3==3.10.12,hostpython3==3.10.12,kivy,arabic_reshaper,python-bidi

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
# p4a.branch = v2024.01.21   # اگه لازم شد؛ ولی چون p4a با pip نصب می‌کنی، بهتره بذاری حذف بمونه

[android]
# مهم: bootstrap باید sdl2 باشه
bootstrap = sdl2
android.build_tools_version = 33.0.2
# API و NDK
android.api = 34
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a

# مجوزها
android.permissions = INTERNET,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PROJECTION,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,POST_NOTIFICATIONS

# فایل‌های Java و Manifest سفارشی
android.add_src = src
android.manifest_path = manifest.xml
android.services = ScreenCaptureService:org.example.screenrecorder.ScreenCaptureService

android.accept_sdk_license = True
