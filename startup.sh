#!/bin/bash

# AgentBot 启动脚本
# 功能: 创建虚拟环境、安装uv、安装依赖

set -e

echo "=========================================="
echo "AgentBot 环境初始化脚本"
echo "=========================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ 检测到 Python 版本: $PYTHON_VERSION"

# 步骤 1: 创建虚拟环境
echo ""
echo "📦 步骤 1: 创建虚拟环境..."
if [ -d "env" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    python3 -m venv env
    echo "✅ 虚拟环境创建成功"
fi

# 步骤 2: 激活虚拟环境
echo ""
echo "🔓 步骤 2: 激活虚拟环境..."
source env/bin/activate
echo "✅ 虚拟环境已激活"

# 步骤 3: 升级pip
echo ""
echo "📥 步骤 3: 升级 pip..."
pip install --upgrade pip setuptools wheel
echo "✅ pip 升级完成"

# 步骤 4: 安装 uv (可选，但推荐使用uv加速)
echo ""
echo "⚡ 步骤 4: 安装 uv..."
if pip show uv &> /dev/null; then
    echo "⚠️  uv 已安装，跳过"
else
    pip install uv
    echo "✅ uv 安装成功"
fi

# 步骤 5: 使用 uv 安装依赖 (如果uv可用) 或直接用pip
echo ""
echo "📚 步骤 5: 安装项目依赖..."
if command -v uv &> /dev/null; then
    echo "🚀 使用 uv 安装依赖 (更快)..."
    uv pip install -r requirements.txt
else
    echo "📥 使用 pip 安装依赖..."
    pip install -r requirements.txt
fi
echo "✅ 依赖安装完成"

# 步骤 6: 创建日志目录
echo ""
echo "📁 步骤 6: 创建日志目录..."
mkdir -p logs
echo "✅ 日志目录已创建"

# 步骤 7: 创建 .env 文件 (如果不存在)
echo ""
echo "⚙️  步骤 7: 检查 .env 配置..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已从 .env.example 创建 .env"
        echo "⚠️  请编辑 .env 文件并填入你的 API 密钥"
    else
        echo "⚠️  .env.example 文件不存在"
    fi
else
    echo "✅ .env 文件已存在"
fi

echo ""
echo "=========================================="
echo "✨ 初始化完成！"
echo "=========================================="
echo ""
echo "接下来的步骤:"
echo "1. 编辑 .env 文件，填入你的 API 密钥"
echo "2. 运行以下命令启动 AgentBot:"
echo "   source env/bin/activate"
echo "   python main.py"
echo ""