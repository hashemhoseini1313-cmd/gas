[app]
title = Screen Recorder
package.name = screenrecorder
package.domain = org.example

source.dir = .
source.include_exts = py,java,png,jpg,kv,ttf,otf

version = 1.0

# نیازمندی‌ها (پایتون و کتابخانه‌ها)
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.2.1,arabic_reshaper,python-bidi,pyjnius

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
p4a.ndk_api= 26
p4a.ndk_version = 25b
[android]
bootstrap = sdl2
android.ndk_api = 26
android.sdk_path = /home/runner/android-sdk
android.skip_update = True
android.build_tools_version = 35.0.0
android.api = 35
android.minapi = 26
android.ndk = 25b
android.arch = arm64-v8a

android.permissions = INTERNET,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PROJECTION,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,POST_NOTIFICATIONS

# فعال‌سازی سرویس جاوا (مهم)
android.add_src = src
android.manifest_path = manifest.xml
#android.services = ScreenCaptureService:org.example.screenrecorder.ScreenCaptureService

android.accept_sdk_license = True
