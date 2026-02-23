[app]
title = Cave of Masters
package.name = caveofmasters
package.domain = org.caveofmasters
source.dir = /root/cave_of_masters
source.include_exts = py,png
version = 1.0.0

orientation = portrait
fullscreen = 1

requirements = python3,kivy,pygame,pyjnius,android,hostpython3

android.permissions = INTERNET,VIBRATE
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
