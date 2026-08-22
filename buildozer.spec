[app]
title = Screen Recorder
package.name = screenrecorder
package.domain = org.example

source.dir = .
source.include_exts = py,java,png,jpg,kv,ttf,otf

version = 1.0

# نیازمندی‌ها (اضافه کردن pyjnius برای استفاده از اندروید)
requirements = python3==3.10.12,kivy==2.3.0,arabic_reshaper,python-bidi,pyjnius

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
bootstrap = sdl2
android.ndk_api = 33
android.sdk_path = /home/runner/android-sdk
android.skip_update = True
android.build_tools_version = 35.0.0
android.api = 35
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a

android.permissions = INTERNET,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PROJECTION,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,POST_NOTIFICATIONS

#android.add_src = src
android.manifest_path = manifest.xml

# ثبت سرویس ضبط صفحه (هماهنگ با workflow)
#android.services = ScreenCaptureService:org.example.screenrecorder.ScreenCaptureService

android.accept_sdk_license = True
