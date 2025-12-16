@echo off
for %%i in (*.jpg *.jpeg *.gif *.bmp) do ren "%%i" "%%~ni.png"