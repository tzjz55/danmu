import re
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import asyncio


# 简单的日志记录器
class Logger:
    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")
    
    @staticmethod
    def error(msg):
        print(f"[ERROR] {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"[WARNING] {msg}")

logger = Logger()


class FilterAction(Enum):
    """过滤动作"""
    ALLOW = "allow"          # 允许
    BLOCK = "block"          # 阻止
    WARNING = "warning"      # 警告
    REPLACE = "replace"      # 替换
    REVIEW = "review"        # 人工审核
    QUARANTINE = "quarantine"  # 隔离


class FilterType(Enum):
    """过滤类型"""
    KEYWORD = "keyword"      # 关键词过滤
    REGEX = "regex"          # 正则表达式过滤
    LENGTH = "length"        # 长度过滤
    RATE_LIMIT = "rate_limit"  # 频率限制
    CONTENT_TYPE = "content_type"  # 内容类型过滤
    USER_LEVEL = "user_level"  # 用户等级过滤
    SENTIMENT = "sentiment"  # 情感分析


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"             # 低风险
    MEDIUM = "medium"       # 中风险
    HIGH = "high"           # 高风险
    CRITICAL = "critical"   # 严重风险


@dataclass
class FilterRule:
    """过滤规则数据类"""
    id: str
    name: str
    filter_type: FilterType
    pattern: str              # 过滤模式（关键词/正则表达式等）
    action: FilterAction
    risk_level: RiskLevel
    replacement: str = ""     # 替换内容
    enabled: bool = True
    priority: int = 1         # 优先级（1-10，10最高）
    description: str = ""
    created_by: int = 0       # 创建者用户ID
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['filter_type'] = self.filter_type.value
        data['action'] = self.action.value
        data['risk_level'] = self.risk_level.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data


@dataclass
class FilterResult:
    """过滤结果数据类"""
    is_blocked: bool = False
    action: FilterAction = FilterAction.ALLOW
    risk_level: RiskLevel = RiskLevel.LOW
    matched_rules: List[str] = None
    original_text: str = ""
    filtered_text: str = ""
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.matched_rules is None:
            self.matched_rules = []
        if self.warnings is None:
            self.warnings = []


class DanmakuContentFilter:
    """弹幕内容过滤器"""
    
    def __init__(self, db_file: str = "data/content_filter.db"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._load_rules()
        self._init_default_rules()
        
        # 缓存编译的正则表达式
        self._regex_cache = {}
        
        # 用户频率限制缓存
        self._rate_limit_cache = {}
        self._rate_limit_window = 60  # 60秒窗口
        
        # 敏感词库
        self._sensitive_words = set()
        self._load_sensitive_words()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 过滤规则表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS filter_rules (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        filter_type TEXT NOT NULL,
                        pattern TEXT NOT NULL,
                        action TEXT NOT NULL,
                        risk_level TEXT NOT NULL,
                        replacement TEXT DEFAULT '',
                        enabled BOOLEAN DEFAULT 1,
                        priority INTEGER DEFAULT 1,
                        description TEXT DEFAULT '',
                        created_by INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 审核记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        original_text TEXT NOT NULL,
                        filtered_text TEXT,
                        action TEXT NOT NULL,
                        risk_level TEXT NOT NULL,
                        matched_rules TEXT,
                        warnings TEXT,
                        审核员_id INTEGER,
                        审核_status TEXT DEFAULT 'pending',
                        审核_notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        审核_at TIMESTAMP
                    )
                ''')
                
                # 敏感词表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sensitive_words (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        word TEXT NOT NULL UNIQUE,
                        category TEXT NOT NULL,
                        severity INTEGER DEFAULT 1,
                        replacement TEXT DEFAULT '***',
                        enabled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_filter_rules_type ON filter_rules(filter_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_filter_rules_enabled ON filter_rules(enabled)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_records_user ON audit_records(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_records_date ON audit_records(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensitive_words_word ON sensitive_words(word)')
                
                conn.commit()
                logger.info("内容过滤数据库初始化完成")
                
        except Exception as e:
            logger.error(f"初始化内容过滤数据库失败: {e}")
            raise
    
    def _load_rules(self):
        """加载过滤规则"""
        self.rules = []
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM filter_rules WHERE enabled = 1 ORDER BY priority DESC')
                
                for row in cursor.fetchall():
                    columns = [desc[0] for desc in cursor.description]
                    data = dict(zip(columns, row))
                    
                    # 转换枚举值
                    data['filter_type'] = FilterType(data['filter_type'])
                    data['action'] = FilterAction(data['action'])
                    data['risk_level'] = RiskLevel(data['risk_level'])
                    
                    if data['created_at']:
                        data['created_at'] = datetime.fromisoformat(data['created_at'])
                    if data['updated_at']:
                        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                    
                    rule = FilterRule(**data)
                    self.rules.append(rule)
                    
                logger.info(f"加载了 {len(self.rules)} 条过滤规则")
                
        except Exception as e:
            logger.error(f"加载过滤规则失败: {e}")
            self.rules = []
    
    def _init_default_rules(self):
        """初始化默认过滤规则"""
        if not self.rules:  # 如果没有规则，创建默认规则
            default_rules = [
                {
                    'id': 'length_limit',
                    'name': '长度限制',
                    'filter_type': FilterType.LENGTH,
                    'pattern': '200',  # 最大200字符
                    'action': FilterAction.BLOCK,
                    'risk_level': RiskLevel.LOW,
                    'description': '限制弹幕最大长度为200字符'
                },
                {
                    'id': 'spam_prevention',
                    'name': '刷屏防护',
                    'filter_type': FilterType.RATE_LIMIT,
                    'pattern': '5,60',  # 60秒内最多5条
                    'action': FilterAction.WARNING,
                    'risk_level': RiskLevel.MEDIUM,
                    'description': '防止用户刷屏'
                },
                {
                    'id': 'ad_filter',
                    'name': '广告过滤',
                    'filter_type': FilterType.REGEX,
                    'pattern': r'(加群|QQ群|微信群|联系方式|电话|手机号)',
                    'action': FilterAction.BLOCK,
                    'risk_level': RiskLevel.HIGH,
                    'description': '过滤广告和联系方式'
                },
                {
                    'id': 'profanity_filter',
                    'name': '脏话过滤',
                    'filter_type': FilterType.KEYWORD,
                    'pattern': '傻逼,智障,脑残,死人,滚蛋',
                    'action': FilterAction.REPLACE,
                    'risk_level': RiskLevel.MEDIUM,
                    'replacement': '***',
                    'description': '过滤不当言论'
                }
            ]
            
            for rule_data in default_rules:
                rule = FilterRule(**rule_data)
                self.add_rule(rule)
    
    def _load_sensitive_words(self):
        """加载敏感词库"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT word FROM sensitive_words WHERE enabled = 1')
                
                self._sensitive_words = {row[0] for row in cursor.fetchall()}
                logger.info(f"加载了 {len(self._sensitive_words)} 个敏感词")
                
        except Exception as e:
            logger.error(f"加载敏感词库失败: {e}")
            self._sensitive_words = set()
    
    def add_rule(self, rule: FilterRule) -> bool:
        """添加过滤规则"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO filter_rules (
                        id, name, filter_type, pattern, action, risk_level,
                        replacement, enabled, priority, description, created_by,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rule.id, rule.name, rule.filter_type.value, rule.pattern,
                    rule.action.value, rule.risk_level.value, rule.replacement,
                    rule.enabled, rule.priority, rule.description, rule.created_by,
                    rule.created_at, rule.updated_at
                ))
                
                conn.commit()
                
                # 重新加载规则
                self._load_rules()
                
                logger.info(f"添加过滤规则成功: {rule.name}")
                return True
                
        except Exception as e:
            logger.error(f"添加过滤规则失败: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除过滤规则"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM filter_rules WHERE id = ?', (rule_id,))
                conn.commit()
                
                # 重新加载规则
                self._load_rules()
                
                logger.info(f"删除过滤规则成功: {rule_id}")
                return True
                
        except Exception as e:
            logger.error(f"删除过滤规则失败: {e}")
            return False
    
    def _check_length_limit(self, text: str, pattern: str) -> bool:
        """检查长度限制"""
        try:
            max_length = int(pattern)
            return len(text) > max_length
        except ValueError:
            return False
    
    def _check_rate_limit(self, user_id: int, pattern: str) -> bool:
        """检查频率限制"""
        try:
            max_count, window_seconds = map(int, pattern.split(','))
            current_time = datetime.now()
            
            # 清理过期记录
            if user_id in self._rate_limit_cache:
                self._rate_limit_cache[user_id] = [
                    timestamp for timestamp in self._rate_limit_cache[user_id]
                    if (current_time - timestamp).total_seconds() < window_seconds
                ]
            else:
                self._rate_limit_cache[user_id] = []
            
            # 检查是否超过限制
            if len(self._rate_limit_cache[user_id]) >= max_count:
                return True
            
            # 记录本次请求
            self._rate_limit_cache[user_id].append(current_time)
            return False
            
        except (ValueError, IndexError):
            return False
    
    def _check_keyword(self, text: str, pattern: str) -> bool:
        """检查关键词"""
        keywords = [kw.strip().lower() for kw in pattern.split(',')]
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                return True
        return False
    
    def _check_regex(self, text: str, pattern: str) -> bool:
        """检查正则表达式"""
        try:
            if pattern not in self._regex_cache:
                self._regex_cache[pattern] = re.compile(pattern, re.IGNORECASE)
            
            regex = self._regex_cache[pattern]
            return bool(regex.search(text))
            
        except re.error as e:
            logger.warning(f"正则表达式错误: {pattern} - {e}")
            return False
    
    def _check_sensitive_words(self, text: str) -> List[str]:
        """检查敏感词"""
        found_words = []
        text_lower = text.lower()
        
        for word in self._sensitive_words:
            if word.lower() in text_lower:
                found_words.append(word)
        
        return found_words
    
    def _apply_replacement(self, text: str, rule: FilterRule) -> str:
        """应用替换规则"""
        if rule.filter_type == FilterType.KEYWORD:
            keywords = [kw.strip() for kw in rule.pattern.split(',')]
            for keyword in keywords:
                text = re.sub(re.escape(keyword), rule.replacement, text, flags=re.IGNORECASE)
        
        elif rule.filter_type == FilterType.REGEX:
            try:
                if rule.pattern not in self._regex_cache:
                    self._regex_cache[rule.pattern] = re.compile(rule.pattern, re.IGNORECASE)
                
                regex = self._regex_cache[rule.pattern]
                text = regex.sub(rule.replacement, text)
                
            except re.error:
                pass
        
        return text
    
    async def filter_content(self, text: str, user_id: int = 0) -> FilterResult:
        """过滤弹幕内容"""
        result = FilterResult(
            original_text=text,
            filtered_text=text
        )
        
        highest_risk = RiskLevel.LOW
        matched_rules = []
        
        try:
            # 按优先级检查规则
            for rule in sorted(self.rules, key=lambda x: x.priority, reverse=True):
                if not rule.enabled:
                    continue
                
                is_matched = False
                
                # 根据规则类型进行检查
                if rule.filter_type == FilterType.LENGTH:
                    is_matched = self._check_length_limit(text, rule.pattern)
                    
                elif rule.filter_type == FilterType.RATE_LIMIT:
                    is_matched = self._check_rate_limit(user_id, rule.pattern)
                    
                elif rule.filter_type == FilterType.KEYWORD:
                    is_matched = self._check_keyword(text, rule.pattern)
                    
                elif rule.filter_type == FilterType.REGEX:
                    is_matched = self._check_regex(text, rule.pattern)
                
                if is_matched:
                    matched_rules.append(rule.id)
                    
                    # 更新风险等级
                    if rule.risk_level.value == 'critical' or highest_risk.value != 'critical':
                        if rule.risk_level.value == 'high' or highest_risk.value not in ['critical', 'high']:
                            if rule.risk_level.value == 'medium' or highest_risk.value == 'low':
                                highest_risk = rule.risk_level
                    
                    # 执行相应动作
                    if rule.action == FilterAction.BLOCK:
                        result.is_blocked = True
                        result.action = FilterAction.BLOCK
                        break
                        
                    elif rule.action == FilterAction.REPLACE:
                        result.filtered_text = self._apply_replacement(result.filtered_text, rule)
                        result.action = FilterAction.REPLACE
                        
                    elif rule.action == FilterAction.WARNING:
                        result.warnings.append(f"触发规则: {rule.name}")
                        result.action = FilterAction.WARNING
                        
                    elif rule.action == FilterAction.REVIEW:
                        result.action = FilterAction.REVIEW
                        break
            
            # 检查敏感词
            sensitive_words = self._check_sensitive_words(text)
            if sensitive_words:
                result.warnings.extend([f"包含敏感词: {word}" for word in sensitive_words])
                if highest_risk == RiskLevel.LOW:
                    highest_risk = RiskLevel.MEDIUM
            
            result.risk_level = highest_risk
            result.matched_rules = matched_rules
            
            # 记录审核日志
            await self._log_audit_record(user_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"内容过滤失败: {e}")
            # 出错时采用保守策略
            return FilterResult(
                is_blocked=True,
                action=FilterAction.REVIEW,
                risk_level=RiskLevel.HIGH,
                original_text=text,
                filtered_text=text,
                warnings=["过滤系统错误，需要人工审核"]
            )
    
    async def _log_audit_record(self, user_id: int, result: FilterResult):
        """记录审核日志"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO audit_records (
                        user_id, original_text, filtered_text, action, risk_level,
                        matched_rules, warnings, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, result.original_text, result.filtered_text,
                    result.action.value, result.risk_level.value,
                    json.dumps(result.matched_rules), json.dumps(result.warnings),
                    datetime.now()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"记录审核日志失败: {e}")
    
    def get_audit_records(self, user_id: Optional[int] = None, days: int = 7) -> List[Dict[str, Any]]:
        """获取审核记录"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                if user_id:
                    cursor.execute('''
                        SELECT * FROM audit_records 
                        WHERE user_id = ? AND created_at BETWEEN ? AND ?
                        ORDER BY created_at DESC
                    ''', (user_id, start_date, end_date))
                else:
                    cursor.execute('''
                        SELECT * FROM audit_records 
                        WHERE created_at BETWEEN ? AND ?
                        ORDER BY created_at DESC
                        LIMIT 100
                    ''', (start_date, end_date))
                
                columns = [desc[0] for desc in cursor.description]
                records = []
                
                for row in cursor.fetchall():
                    record = dict(zip(columns, row))
                    
                    # 解析 JSON 字段
                    if record['matched_rules']:
                        record['matched_rules'] = json.loads(record['matched_rules'])
                    if record['warnings']:
                        record['warnings'] = json.loads(record['warnings'])
                    
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"获取审核记录失败: {e}")
            return []
    
    def get_filter_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取过滤统计信息"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # 总体统计
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_processed,
                        SUM(CASE WHEN action = 'block' THEN 1 ELSE 0 END) as blocked,
                        SUM(CASE WHEN action = 'warning' THEN 1 ELSE 0 END) as warned,
                        SUM(CASE WHEN action = 'replace' THEN 1 ELSE 0 END) as replaced,
                        SUM(CASE WHEN action = 'review' THEN 1 ELSE 0 END) as needs_review
                    FROM audit_records
                    WHERE created_at BETWEEN ? AND ?
                ''', (start_date, end_date))
                
                stats = cursor.fetchone()
                
                # 风险等级分布
                cursor.execute('''
                    SELECT risk_level, COUNT(*) 
                    FROM audit_records
                    WHERE created_at BETWEEN ? AND ?
                    GROUP BY risk_level
                ''', (start_date, end_date))
                
                risk_distribution = dict(cursor.fetchall())
                
                # 最活跃用户
                cursor.execute('''
                    SELECT user_id, COUNT(*) as count
                    FROM audit_records
                    WHERE created_at BETWEEN ? AND ?
                    GROUP BY user_id
                    ORDER BY count DESC
                    LIMIT 10
                ''', (start_date, end_date))
                
                top_users = cursor.fetchall()
                
                return {
                    'period_days': days,
                    'total_processed': stats[0] or 0,
                    'blocked': stats[1] or 0,
                    'warned': stats[2] or 0,
                    'replaced': stats[3] or 0,
                    'needs_review': stats[4] or 0,
                    'risk_distribution': risk_distribution,
                    'top_users': [{'user_id': uid, 'count': count} for uid, count in top_users],
                    'active_rules': len(self.rules),
                    'sensitive_words_count': len(self._sensitive_words)
                }
                
        except Exception as e:
            logger.error(f"获取过滤统计失败: {e}")
            return {}
    
    def add_sensitive_word(self, word: str, category: str = "general", severity: int = 1) -> bool:
        """添加敏感词"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO sensitive_words (word, category, severity)
                    VALUES (?, ?, ?)
                ''', (word, category, severity))
                
                conn.commit()
                
                # 重新加载敏感词
                self._load_sensitive_words()
                
                logger.info(f"添加敏感词成功: {word}")
                return True
                
        except Exception as e:
            logger.error(f"添加敏感词失败: {e}")
            return False
    
    def remove_sensitive_word(self, word: str) -> bool:
        """删除敏感词"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM sensitive_words WHERE word = ?', (word,))
                conn.commit()
                
                # 重新加载敏感词
                self._load_sensitive_words()
                
                logger.info(f"删除敏感词成功: {word}")
                return True
                
        except Exception as e:
            logger.error(f"删除敏感词失败: {e}")
            return False
    
    def clear_cache(self):
        """清理缓存"""
        self._regex_cache.clear()
        self._rate_limit_cache.clear()
        logger.info("已清理过滤器缓存")


# 全局内容过滤器实例
content_filter = DanmakuContentFilter()