# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# 项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(SPECPATH)))

block_cipher = None

a = Analysis(
    ['mark2video_gui.py'],
    pathex=[project_root],  # 添加项目根目录到路径
    binaries=[],
    datas=[
        # 包含 povideo 模块
        (os.path.join(project_root, 'povideo'), 'povideo'),
    ],
    hiddenimports=[
        'povideo',
        'povideo.api',
        'povideo.api.video',
        'povideo.core',
        'povideo.core.VideoType',
        'povideo.lib',
        'povideo.lib.tencent',
        'povideo.lib.tencent.audio2txt_service',
        'moviepy',
        'moviepy.editor',
        'moviepy.video',
        'moviepy.video.io',
        'moviepy.video.io.VideoFileClip',
        'moviepy.video.compositing',
        'moviepy.video.compositing.CompositeVideoClip',
        'moviepy.video.VideoClip',
        'moviepy.audio',
        'imageio',
        'imageio_ffmpeg',
        'proglog',
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Mark2Video_Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # 如果有图标文件，取消注释此行
)
