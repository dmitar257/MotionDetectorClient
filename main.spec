# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

import sys
import os

path = os.path.abspath(".")


a = Analysis(['main.py'],
             pathex=[path],
             binaries=[],
             datas=[('detectionstream.kv', '.')],
             hiddenimports=[],
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='MovementDetectionClient',
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          disable_windowed_traceback=False,
          debug=False,
          console=False )
