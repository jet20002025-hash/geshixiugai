"""
存储基类接口
定义所有存储后端必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class StorageBase(ABC):
    """存储基类，所有存储后端必须继承此类"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查存储是否可用"""
        pass
    
    @abstractmethod
    def upload_file(self, key: str, file_obj: BinaryIO) -> bool:
        """上传文件"""
        pass
    
    @abstractmethod
    def download_file(self, key: str) -> Optional[bytes]:
        """下载文件"""
        pass
    
    @abstractmethod
    def file_exists(self, key: str) -> bool:
        """检查文件是否存在"""
        pass
    
    @abstractmethod
    def delete_file(self, key: str) -> bool:
        """删除文件"""
        pass

