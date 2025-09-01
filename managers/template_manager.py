import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger


class DanmakuTemplateManager:
    """弹幕模板管理器"""
    
    def __init__(self, template_file: str = "data/danmaku_templates.json"):
        self.template_file = Path(template_file)
        self.templates: Dict[str, Dict] = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载弹幕模板"""
        try:
            if self.template_file.exists():
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            else:
                # 创建默认模板
                self._create_default_templates()
                self._save_templates()
        except Exception as e:
            logger.error(f"加载弹幕模板失败: {e}")
            self._create_default_templates()
    
    def _create_default_templates(self):
        """创建默认弹幕模板"""
        self.templates = {
            "欢迎": {
                "text": "欢迎来到直播间！",
                "color": "#00FF00",
                "position": "top",
                "font_size": 26,
                "duration": 6,
                "category": "greeting"
            },
            "感谢关注": {
                "text": "感谢关注！",
                "color": "#FFD700",
                "position": "scroll",
                "font_size": 24,
                "duration": 5,
                "category": "thanks"
            },
            "精彩": {
                "text": "太精彩了！",
                "color": "#FF69B4",
                "position": "scroll",
                "font_size": 24,
                "duration": 5,
                "category": "reaction"
            },
            "666": {
                "text": "666666",
                "color": "#FF0000",
                "position": "scroll",
                "font_size": 28,
                "duration": 4,
                "category": "reaction"
            },
            "警告": {
                "text": "⚠️ 请注意内容规范",
                "color": "#FF8C00",
                "position": "top",
                "font_size": 26,
                "duration": 8,
                "category": "warning"
            },
            "活动开始": {
                "text": "🎉 活动开始啦！",
                "color": "#9370DB",
                "position": "top",
                "font_size": 30,
                "duration": 10,
                "category": "event"
            },
            "抽奖": {
                "text": "🎁 抽奖时间到！",
                "color": "#FF1493",
                "position": "top",
                "font_size": 28,
                "duration": 8,
                "category": "event"
            },
            "互动": {
                "text": "大家快来互动吧！",
                "color": "#00CED1",
                "position": "scroll",
                "font_size": 24,
                "duration": 6,
                "category": "interaction"
            }
        }
    
    def _save_templates(self):
        """保存弹幕模板"""
        try:
            self.template_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.template_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存弹幕模板失败: {e}")
    
    def get_template(self, name: str) -> Optional[Dict]:
        """获取模板"""
        return self.templates.get(name)
    
    def get_templates_by_category(self, category: str) -> Dict[str, Dict]:
        """按分类获取模板"""
        return {
            name: template for name, template in self.templates.items()
            if template.get('category') == category
        }
    
    def get_all_templates(self) -> Dict[str, Dict]:
        """获取所有模板"""
        return self.templates.copy()
    
    def get_template_names(self) -> List[str]:
        """获取所有模板名称"""
        return list(self.templates.keys())
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for template in self.templates.values():
            if 'category' in template:
                categories.add(template['category'])
        return sorted(list(categories))
    
    def add_template(
        self, 
        name: str, 
        text: str,
        color: str = "#FFFFFF",
        position: str = "scroll",
        font_size: int = 24,
        duration: int = 5,
        category: str = "custom"
    ) -> bool:
        """添加新模板"""
        try:
            self.templates[name] = {
                "text": text,
                "color": color,
                "position": position,
                "font_size": font_size,
                "duration": duration,
                "category": category
            }
            self._save_templates()
            return True
        except Exception as e:
            logger.error(f"添加模板失败: {e}")
            return False
    
    def update_template(self, name: str, **kwargs) -> bool:
        """更新模板"""
        try:
            if name not in self.templates:
                return False
            
            self.templates[name].update(kwargs)
            self._save_templates()
            return True
        except Exception as e:
            logger.error(f"更新模板失败: {e}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """删除模板"""
        try:
            if name in self.templates:
                del self.templates[name]
                self._save_templates()
                return True
            return False
        except Exception as e:
            logger.error(f"删除模板失败: {e}")
            return False
    
    def search_templates(self, keyword: str) -> Dict[str, Dict]:
        """搜索模板"""
        results = {}
        keyword = keyword.lower()
        
        for name, template in self.templates.items():
            if (keyword in name.lower() or 
                keyword in template.get('text', '').lower() or
                keyword in template.get('category', '').lower()):
                results[name] = template
        
        return results
    
    def export_templates(self, file_path: str) -> bool:
        """导出模板"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"导出模板失败: {e}")
            return False
    
    def import_templates(self, file_path: str, merge: bool = True) -> bool:
        """导入模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_templates = json.load(f)
            
            if merge:
                self.templates.update(imported_templates)
            else:
                self.templates = imported_templates
            
            self._save_templates()
            return True
        except Exception as e:
            logger.error(f"导入模板失败: {e}")
            return False


# 全局模板管理器实例
template_manager = DanmakuTemplateManager()