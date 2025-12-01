"""
大学预设模板服务
提供常见大学的毕业论文格式模板配置
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

# 获取当前文件所在目录
CURRENT_DIR = Path(__file__).parent
TEMPLATES_FILE = CURRENT_DIR / "university_templates.json"


class UniversityTemplateService:
    """大学预设模板服务"""
    
    def __init__(self, templates_file: Optional[Path] = None):
        """
        初始化服务
        
        Args:
            templates_file: 模板配置文件路径，默认使用同目录下的 university_templates.json
        """
        self.templates_file = templates_file or TEMPLATES_FILE
        self._templates_cache: Optional[Dict] = None
    
    def _load_templates(self) -> Dict:
        """加载模板配置"""
        if self._templates_cache is not None:
            return self._templates_cache
        
        if not self.templates_file.exists():
            # 如果文件不存在，返回空配置
            self._templates_cache = {"universities": []}
            return self._templates_cache
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                self._templates_cache = json.load(f)
            return self._templates_cache
        except (json.JSONDecodeError, IOError) as e:
            # 如果读取失败，返回空配置
            print(f"Warning: Failed to load university templates: {e}")
            self._templates_cache = {"universities": []}
            return self._templates_cache
    
    def get_all_universities(self) -> List[Dict]:
        """
        获取所有大学列表
        
        Returns:
            大学列表，每个包含 id, name, display_name, description
        """
        templates = self._load_templates()
        universities = templates.get("universities", [])
        
        # 只返回基本信息，不包含详细的 parameters
        return [
            {
                "id": uni.get("id"),
                "name": uni.get("name"),
                "display_name": uni.get("display_name", uni.get("name")),
                "description": uni.get("description", ""),
            }
            for uni in universities
        ]
    
    def get_university_template(self, university_id: str) -> Optional[Dict]:
        """
        获取指定大学的模板配置
        
        Args:
            university_id: 大学ID（如 "tsinghua", "pku"）
            
        Returns:
            模板配置字典，包含 parameters，如果不存在返回 None
        """
        templates = self._load_templates()
        universities = templates.get("universities", [])
        
        for uni in universities:
            if uni.get("id") == university_id:
                return {
                    "id": uni.get("id"),
                    "name": uni.get("name"),
                    "display_name": uni.get("display_name", uni.get("name")),
                    "description": uni.get("description", ""),
                    "parameters": uni.get("parameters", {}),
                }
        
        return None
    
    def get_university_parameters(self, university_id: str) -> Optional[Dict]:
        """
        获取指定大学的格式参数（仅参数部分）
        
        Args:
            university_id: 大学ID
            
        Returns:
            参数字典，如果不存在返回 None
        """
        template = self.get_university_template(university_id)
        if template:
            return template.get("parameters", {})
        return None
    
    def search_universities(self, keyword: str) -> List[Dict]:
        """
        搜索大学（按名称或描述）
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的大学列表
        """
        all_universities = self.get_all_universities()
        keyword_lower = keyword.lower()
        
        return [
            uni for uni in all_universities
            if keyword_lower in uni.get("name", "").lower()
            or keyword_lower in uni.get("display_name", "").lower()
            or keyword_lower in uni.get("description", "").lower()
        ]




