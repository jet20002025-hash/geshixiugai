"""
存储辅助函数
提供文件保存和读取的便捷方法，支持本地文件系统和云存储
"""
import io
import json
from pathlib import Path
from typing import Optional, Dict, Any
from .storage_factory import get_storage


class StorageHelper:
    """存储辅助类，统一处理本地和云存储"""
    
    def __init__(self, use_storage: bool = True):
        """
        初始化存储辅助类
        
        Args:
            use_storage: 是否使用云存储（如果可用）
        """
        self.storage = get_storage() if use_storage else None
        self.use_storage = use_storage and self.storage is not None
    
    def save_file(self, key: str, content: bytes) -> bool:
        """
        保存文件
        
        Args:
            key: 文件键（路径）
            content: 文件内容（字节）
        
        Returns:
            是否成功
        """
        if self.use_storage:
            # 使用云存储
            file_obj = io.BytesIO(content)
            return self.storage.upload_file(key, file_obj)
        else:
            # 使用本地文件系统
            file_path = Path(key)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)
            return True
    
    def load_file(self, key: str) -> Optional[bytes]:
        """
        加载文件
        
        Args:
            key: 文件键（路径）
        
        Returns:
            文件内容（字节），如果不存在则返回 None
        """
        if self.use_storage:
            # 使用云存储
            return self.storage.download_file(key)
        else:
            # 使用本地文件系统
            file_path = Path(key)
            if not file_path.exists():
                return None
            return file_path.read_bytes()
    
    def file_exists(self, key: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            key: 文件键（路径）
        
        Returns:
            是否存在
        """
        if self.use_storage:
            # 使用云存储
            return self.storage.file_exists(key)
        else:
            # 使用本地文件系统
            return Path(key).exists()
    
    def save_json(self, key: str, data: Dict[str, Any]) -> bool:
        """
        保存 JSON 文件
        
        Args:
            key: 文件键（路径）
            data: JSON 数据
        
        Returns:
            是否成功
        """
        content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        return self.save_file(key, content)
    
    def load_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        加载 JSON 文件
        
        Args:
            key: 文件键（路径）
        
        Returns:
            JSON 数据，如果不存在则返回 None
        """
        content = self.load_file(key)
        if content is None:
            return None
        return json.loads(content.decode("utf-8"))
    
    def delete_file(self, key: str) -> bool:
        """
        删除文件
        
        Args:
            key: 文件键（路径）
        
        Returns:
            是否成功
        """
        if self.use_storage:
            # 使用云存储
            return self.storage.delete_file(key)
        else:
            # 使用本地文件系统
            file_path = Path(key)
            if file_path.exists():
                file_path.unlink()
                return True
            return False

