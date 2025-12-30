@echo off
chcp 65001 >nul
echo ========================================
echo   视频水印工具 - 打包脚本
echo ========================================
echo.

REM 检查 PyInstaller 是否安装
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] 正在安装 PyInstaller...
    pip install pyinstaller -i https://mirrors.aliyun.com/pypi/simple/
)

echo [INFO] 开始打包...
echo.

cd /d %~dp0

REM 清理之前的构建
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 使用 spec 文件打包
pyinstaller build_exe.spec --clean

echo.
if exist "dist\Mark2Video_Tool.exe" (
    echo ========================================
    echo   打包成功！
    echo   输出位置: dist\Mark2Video_Tool.exe
    echo ========================================
) else (
    echo [ERROR] 打包失败，请检查错误信息
)

pause
