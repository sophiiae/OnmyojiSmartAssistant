#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def test_exe_build():
    """测试exe构建"""
    print("开始测试exe构建...")

    # 检查必要文件是否存在
    required_files = [
        '../config_editor/osa_editor.py',
        '../main.py',
        '../requirements.txt',
        '../configs/osa.json'
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"错误：缺少必要文件 {file}")
            return False

    print("✓ 所有必要文件存在")

    # 检查Python环境
    try:
        import PyQt6
        print("✓ PyQt6已安装")
    except ImportError:
        print("错误：PyQt6未安装")
        return False

    # 尝试导入主要模块
    try:
        import sys
        sys.path.append('..')
        from config_editor.osa_editor import OSAEditor, ConfigEditor
        print("✓ 主要模块导入成功")
    except Exception as e:
        print(f"错误：模块导入失败 - {e}")
        return False

    print("✓ 所有测试通过，可以开始构建exe")
    return True


if __name__ == "__main__":
    if test_exe_build():
        print("\n可以运行以下命令构建exe：")
        print("python build_exe.py")
        print("或者双击 build.bat")
    else:
        print("\n请先解决上述问题再构建exe")
