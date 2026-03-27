# -*- mode: python ; coding: utf-8 -*-

"""
Arquivo de configuração PyInstaller para gerar executável do PingTest.
Execute: pyinstaller build_exe.spec
"""

import sys
from pathlib import Path

# Nome do executável
app_name = 'PingTest'

# Coletar módulos hidden imports do Streamlit
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'pandas',
    'pyautogui',
    'numpy',
    'altair',
    'toml',
    'validators',
    'watchdog',
    'cachetools',
    'pympler',
    'semver',
    'gitdb',
    'smmap',
]

# Dados adicionais necessários (Streamlit precisa de seus arquivos estáticos)
datas = []

# Tentar encontrar diretório de instalação do Streamlit
try:
    import streamlit as st
    st_path = Path(st.__file__).parent
    
    # Adicionar static files do Streamlit
    datas.append((str(st_path / 'static'), 'streamlit/static'))
    datas.append((str(st_path / 'runtime'), 'streamlit/runtime'))
except ImportError:
    print("Aviso: Streamlit não encontrado. Instale com: pip install streamlit")

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Manter console para ver logs do Streamlit
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione um ícone .ico aqui se desejar
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)

# Nota: Para criar um executável de arquivo único, use:
# exe = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     [],
#     name=app_name,
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=True,
# )
