[app]

title = ??? ????
package.name = screenrecorder
package.domain = org.example

source.dir = .
source.include_exts = py,java,png,jpg,kv

version = 1.0

requirements = python3,kivy==2.2.1,cython==0.29.36

orientation = portrait

fullscreen = 0
max_cores = 1
android.api = 33
android.minapi = 21
android.ndk = 25b

android.permissions = INTERNET,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PROJECTION

android.archs = arm64-v8a

android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
