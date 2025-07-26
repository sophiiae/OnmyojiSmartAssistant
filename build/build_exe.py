import os
import sys
import subprocess
import shutil

def build_exe():
    """构建exe程序"""

    # 确保PyInstaller已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 创建spec文件内容
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../config_editor/osa_editor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../configs', 'configs'),
        ('../tasks', 'tasks'),
        ('../module', 'module'),
        ('../data', 'data'),
        ('../logs', 'logs'),
        ('../main.py', '.'),
        ('../activity.py', '.'),
        ('../capture.py', '.'),
        ('../colla.py', '.'),
        ('../errand.py', '.'),
        ('../match.py', '.'),
        ('../royal_battle.py', '.'),
        ('../test.py', '.'),
        ('../run.bat', '.'),
        ('../README.md', '.'),
        ('../USAGE.md', '.'),
        ('../venv/Lib/site-packages/ppocronnx', 'ppocronnx'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'cv2',
        'numpy',
        'PIL',
        'requests',
        'psutil',
        'pyautogui',
        'pydantic',
        'tqdm',
        'coloredlogs',
        'colorama',
        'pure_python_adb',
        'ppocronnx',
        'onnxruntime',
        'shapely',
        'sympy',
        'mpmath',
        'inflection',
        'typing_inspection',
        'annotated_types',
        'pydantic_core',
        'typing_extensions',
        'packaging',
        'certifi',
        'charset_normalizer',
        'idna',
        'urllib3',
        'humanfriendly',
        'flatbuffers',
        'protobuf',
        'pefile',
        'altgraph',
        'MouseInfo',
        'PyGetWindow',
        'PyMsgBox',
        'pyperclip',
        'PyRect',
        'PyScreeze',
        'pytweening',
        'pyreadline3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['trifle_fairy', 'fairy_editor', 'tkinter', 'matplotlib', 'scipy'],
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
    name='OSA',
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
    icon=None,
    distpath='.',
)
'''

    # 写入spec文件
    with open('osa_editor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("开始构建exe程序...")

    # 运行PyInstaller
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "osa_editor.spec"
        ])

        print("构建完成！")
        print("exe文件位置: ./OSA.exe")

        # 清理临时文件
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('osa_editor.spec'):
            os.remove('osa_editor.spec')

        # 将生成的exe文件移动到上级目录（项目根目录）
        if os.path.exists('dist/OSA.exe'):
            target_path = '../OSA.exe'
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)  # 删除旧的exe文件
                except PermissionError:
                    print("警告：无法删除旧的OSA.exe文件，可能正在运行中")
                    print("请关闭OSA.exe程序后重新构建")
                    return
            shutil.move('dist/OSA.exe', target_path)
            print("exe文件已移动到项目根目录")

    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

    return True


if __name__ == "__main__":
    print("OSA项目exe构建工具")
    print("=" * 50)

    print("构建OSA配置编辑器 (包含脚本运行功能)")
    build_exe()
