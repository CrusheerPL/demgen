# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('imagecodecs')

# jeżeli po uruchomieniu 'demgen.exe' pojawi się komunikat z błędem "cannot import name 'Blosc' from 'numcodecs'" - usunąć znacznik komentarza z linii nr 10
# if this error message appears after starting the 'demgen.exe' executable: "cannot import name 'Blosc' from 'numcodecs'" - remove the comment mark from the line nr 10

# hiddenimports += collect_submodules('numcodecs')


block_cipher = None


a = Analysis(
    ['demgen.py'],
    pathex=[],
    binaries=[],
    datas=[('favicon.ico', '.')],
    hiddenimports=hiddenimports,
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
    [('v', None, 'OPTION')],
    name='demgen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
)
