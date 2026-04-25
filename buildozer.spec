[app]
title = MyPingo Parent
package.name = pingo_parent
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav
version = 0.1
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1