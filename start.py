#!/usr/bin/env python3
"""
快速启动脚本
用于本地开发和测试
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查 .env 文件
    if not Path('.env').exists():
        print("❌ .env 文件不存在")
        print("📝 请复制 .env.example 到 .env 并配置相关参数")
        if Path('.env.example').exists():
            print("💡 运行命令: cp .env.example .env")
        return False
    
    # 检查必要目录
    Path('data').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    print("✅ 环境检查通过")
    return True

def install_dependencies():
    """安装依赖包"""
    print("📦 安装Python依赖包...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def start_bot():
    """启动机器人"""
    print("🚀 启动Telegram机器人...")
    
    try:
        # 直接运行 bot.py
        subprocess.run([sys.executable, 'bot.py'], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  机器人已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 机器人启动失败: {e}")

def main():
    """主函数"""
    print("🎮 Telegram 弹幕控制机器人 - 快速启动")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        return
    
    # 检查是否安装依赖
    if '--skip-install' not in sys.argv:
        if not install_dependencies():
            return
    
    # 启动机器人
    start_bot()

if __name__ == "__main__":
    main()