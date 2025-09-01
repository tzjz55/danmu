#!/usr/bin/env python3
"""
项目测试脚本
检查所有组件是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

async def test_config():
    """测试配置"""
    print("🔧 测试配置...")
    try:
        from config import config
        config.validate()
        print("✅ 配置验证通过")
        return True
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

async def test_database():
    """测试数据库"""
    print("🗄️  测试数据库...")
    try:
        from managers.user_manager import user_manager
        await user_manager.init_database()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

async def test_api_clients():
    """测试API客户端"""
    print("🌐 测试API客户端...")
    try:
        from clients.danmaku_client import danmaku_client
        from clients.tmdb_client import tmdb_client
        
        # 测试弹幕API（不实际调用，只检查初始化）
        print("  - 弹幕API客户端初始化: ✅")
        
        # 测试TMDB API（不实际调用，只检查初始化）
        print("  - TMDB API客户端初始化: ✅")
        
        return True
    except Exception as e:
        print(f"❌ API客户端测试失败: {e}")
        return False

async def test_handlers():
    """测试处理器"""
    print("🎛️  测试处理器...")
    try:
        from handlers import commands, callbacks
        from utils.keyboards import keyboards
        
        # 检查处理器函数存在
        assert hasattr(commands, 'start_command')
        assert hasattr(callbacks, 'button_callback_handler')
        assert hasattr(keyboards, 'main_menu')
        
        print("✅ 处理器测试通过")
        return True
    except Exception as e:
        print(f"❌ 处理器测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 开始项目测试")
    print("=" * 50)
    
    tests = [
        test_config,
        test_database,
        test_api_clients,
        test_handlers
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()
    
    # 统计结果
    passed = sum(results)
    total = len(results)
    
    print("📊 测试结果")
    print("=" * 50)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！项目可以正常运行。")
        print("\n🚀 启动命令:")
        print("  python start.py        # 本地启动")
        print("  ./deploy.sh start      # Docker启动")
    else:
        print("❌ 部分测试失败，请检查配置和依赖。")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())