# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('config.json', '.'), ('resources', 'resources'), ('ui/styles.qss', 'ui')]
binaries = []
hiddenimports = [
    'paramiko',
    'paramiko.transport',
    'paramiko.auth_handler',
    'paramiko.channel',
    'paramiko.client',
    'paramiko.ecdsakey',
    'paramiko.ed25519key',
    'paramiko.hostkeys',
    'paramiko.kex_curve25519',
    'paramiko.kex_ecdh_nist',
    'paramiko.kex_gex',
    'paramiko.kex_group1',
    'paramiko.kex_group14',
    'paramiko.kex_group16',
    'paramiko.packet',
    'paramiko.sftp_client',
    'cryptography',
    'cryptography.hazmat.primitives.ciphers.algorithms',
    'cryptography.hazmat.primitives.ciphers.modes',
    'cryptography.hazmat.backends.openssl',
]
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'test'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RetroArch Rom Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\gamepad.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RetroArch Rom Manager',
)
