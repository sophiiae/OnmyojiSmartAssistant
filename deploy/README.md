# OSA.exe 生成说明

## 概述
本文件夹包含生成 `osa.exe` 可执行文件所需的所有配置文件和脚本。

## 文件说明

### 核心文件
- **`osa_launcher.bat`** - 批处理启动脚本
  - 设置工作目录为项目根目录
  - 检查虚拟环境并启动Python程序
  - 直接调用Python程序启动OSA配置编辑器

- **`osa_final.SED`** - IExpress配置文件
  - 配置exe文件的生成参数
  - 设置 `AppLaunched=cmd /c "cd /d E:\dev\onmyoji-sa && deploy\osa_launcher.bat"`
  - 显示安装程序窗口（`ShowInstallProgramWindow=1`）

## 生成步骤

### 1. 准备工作
确保项目根目录包含以下文件：
- `config_editor/` 目录（包含OSA配置编辑器）
- `venv/` 目录（Python虚拟环境）
- `requirements.txt`（Python依赖）

### 2. 生成exe文件
在项目根目录执行以下命令：
```bash
iexpress /n deploy/osa_final.SED
```

### 3. 验证结果
- 生成的 `osa.exe` 文件将位于项目根目录
- 双击 `osa.exe` 应该直接启动OSA配置编辑器
- 会显示cmd窗口但程序能正常工作

## 技术细节

### 批处理脚本特点
- 使用绝对路径设置工作目录
- 自动检测虚拟环境路径
- 直接调用Python程序，无额外窗口

### SED文件配置
- `ShowInstallProgramWindow=1` - 显示安装程序窗口
- `HideExtractAnimation=1` - 隐藏解压动画
- `AppLaunched=cmd /c "cd /d E:\dev\onmyoji-sa && deploy\osa_launcher.bat"` - 使用cmd启动批处理文件

## 故障排除

### 如果exe文件无法启动
1. 检查 `venv/Scripts/python.exe` 是否存在
2. 确认 `config_editor/main.py` 文件存在
3. 验证项目根目录路径是否正确

### 如果出现弹窗
1. 确认 `osa_launcher.bat` 文件在正确位置
2. 检查项目路径是否正确（当前设置为 `E:\dev\onmyoji-sa`）
3. 验证SED文件中的路径配置

## 更新流程

### 修改启动脚本
1. 编辑 `deploy/osa_launcher.bat`
2. 根据需要修改Python启动参数或项目路径
3. 重新生成exe文件

### 修改SED配置
1. 编辑 `deploy/osa_final.SED`
2. 调整窗口显示设置
3. 重新生成exe文件

## 注意事项
- 生成的exe文件依赖于项目目录结构
- 不要移动或删除项目根目录中的 `venv/` 和 `config_editor/` 目录
- 如果需要分发exe文件，需要确保目标机器有相应的Python环境
- 当前配置使用绝对路径 `E:\dev\onmyoji-sa`，如需修改请更新 `osa_launcher.bat` 文件
- exe文件启动时会显示cmd窗口，但程序能正常工作 