[app]
title = گیاهیار - مراقبت از گیاهان
package.name = plantcare
package.domain = com.giaahyar

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf
source.include_patterns = images/*.png,images/*.jpg,images/*.jpeg,data/*.py,screens/*.py,components/*.py,utils/*.py

version = 1.0.0

requirements = python3,kivy==2.3.0,pillow,requests

orientation = portrait
fullscreen = 0

android.minapi = 21
android.ndk = 27.3.13750724
android.sdk = 33
android.ndk_api = 21
android.arch = arm64-v8a

android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA,VIBRATE

icon.filename = %(source.dir)s/images/app_icon.png
presplash.filename = %(source.dir)s/images/splash.jpg
android.presplash_color = #2E7D32

android.accept_sdk_license = True
android.logcat_filters = *:S python:D
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
