#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
弹幕过滤审核功能演示脚本
演示内容过滤器的各项功能
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from managers.content_filter import (
    content_filter, 
    FilterType, 
    FilterAction, 
    RiskLevel, 
    FilterRule
)


async def demo_content_filtering():
    """演示内容过滤功能"""
    print("=" * 60)
    print("🛡️  弹幕内容过滤与审核系统演示")
    print("=" * 60)
    print()
    
    # 1. 显示当前加载的规则
    print("📋 当前过滤规则:")
    print(f"   共加载 {len(content_filter.rules)} 条规则")
    for i, rule in enumerate(content_filter.rules, 1):
        print(f"   {i}. {rule.name} ({rule.filter_type.value}) - {rule.action.value}")
    print()
    
    # 2. 测试各种过滤场景
    test_cases = [
        ("正常弹幕", "这是一条正常的弹幕内容"),
        ("长度超限", "这是一条超级长的弹幕" + "内容" * 50),
        ("包含脏话", "这个主播真的是傻逼"),
        ("广告内容", "快来加我QQ群123456789"),
        ("联系方式", "我的微信号是abc123"),
        ("正常评论", "主播唱得真好听"),
        ("重复刷屏", "666666666666"),
    ]
    
    print("🧪 内容过滤测试:")
    print("-" * 40)
    
    for desc, text in test_cases:
        result = await content_filter.filter_content(text, user_id=12345)
        
        status_icon = "❌" if result.is_blocked else "✅"
        action_desc = {
            'allow': '允许通过',
            'block': '已拦截',
            'warning': '警告',
            'replace': '内容替换',
            'review': '待审核'
        }.get(result.action.value, result.action.value)
        
        print(f"{status_icon} {desc}:")
        print(f"   原文: {text[:30]}{'...' if len(text) > 30 else ''}")
        print(f"   结果: {action_desc}")
        print(f"   风险: {result.risk_level.value.upper()}")
        
        if result.filtered_text != text:
            print(f"   过滤后: {result.filtered_text[:30]}{'...' if len(result.filtered_text) > 30 else ''}")
        
        if result.warnings:
            print(f"   警告: {', '.join(result.warnings)}")
        
        if result.matched_rules:
            print(f"   触发规则: {', '.join(result.matched_rules)}")
        
        print()
    
    # 3. 显示过滤统计
    print("📊 过滤统计信息:")
    print("-" * 40)
    stats = content_filter.get_filter_statistics(days=1)
    
    print(f"今日处理: {stats.get('total_processed', 0)} 条")
    print(f"已拦截: {stats.get('blocked', 0)} 条")
    print(f"已警告: {stats.get('warned', 0)} 条") 
    print(f"已替换: {stats.get('replaced', 0)} 条")
    print(f"待审核: {stats.get('needs_review', 0)} 条")
    print()
    
    # 4. 演示添加自定义规则
    print("🔧 添加自定义过滤规则:")
    print("-" * 40)
    
    custom_rule = FilterRule(
        id="custom_emoji_filter",
        name="表情符号过滤",
        filter_type=FilterType.REGEX,
        pattern=r"[😀-🙏]{3,}",  # 连续3个或以上表情符号
        action=FilterAction.WARNING,
        risk_level=RiskLevel.LOW,
        description="过滤连续表情符号刷屏",
        created_by=1
    )
    
    success = content_filter.add_rule(custom_rule)
    if success:
        print("✅ 自定义规则添加成功")
        
        # 测试新规则
        emoji_test = "主播好棒 😀😀😀😀😀"
        result = await content_filter.filter_content(emoji_test, user_id=12345)
        print(f"测试表情符号: {result.action.value}")
        if result.warnings:
            print(f"警告信息: {', '.join(result.warnings)}")
    else:
        print("❌ 自定义规则添加失败")
    print()
    
    # 5. 显示审核记录
    print("📝 审核记录:")
    print("-" * 40)
    records = content_filter.get_audit_records(days=1)
    
    if records:
        print(f"今日审核记录 {len(records)} 条:")
        for i, record in enumerate(records[:5], 1):  # 只显示前5条
            action_icon = {
                'block': '🚫',
                'warning': '⚠️',
                'replace': '🔄',
                'review': '👁️',
                'allow': '✅'
            }.get(record['action'], '❓')
            
            print(f"  {i}. {action_icon} {record['original_text'][:25]}...")
            print(f"     风险: {record['risk_level']} | 动作: {record['action']}")
    else:
        print("暂无审核记录")
    print()
    
    # 6. 显示系统信息
    print("ℹ️  系统信息:")
    print("-" * 40)
    print(f"活跃规则数: {len(content_filter.rules)}")
    print(f"敏感词数量: {len(content_filter._sensitive_words)}")
    print(f"正则缓存: {len(content_filter._regex_cache)} 个")
    print(f"频率限制缓存: {len(content_filter._rate_limit_cache)} 个用户")
    print()
    
    print("🎉 弹幕过滤审核系统演示完成!")
    print("=" * 60)


def main():
    """主函数"""
    try:
        asyncio.run(demo_content_filtering())
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())