"""
Supabase Storage 存储适配器
用于替代本地文件系统存储
"""
import os
import httpx
from urllib.parse import quote
from typing import BinaryIO, Optional
from .storage_base import StorageBase


class SupabaseStorage(StorageBase):
    """Supabase Storage 存储类"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL', '').rstrip('/')
        self.key = os.getenv('SUPABASE_KEY', '')  # service_role key
        self.bucket_name = os.getenv('SUPABASE_BUCKET', 'word-formatter-storage')
        
        # 构建 API 基础 URL
        if self.url:
            self.api_url = f"{self.url}/storage/v1"
        else:
            self.api_url = None
    
    def is_available(self) -> bool:
        """检查 Supabase 存储是否可用"""
        return bool(self.url and self.key and self.api_url)
    
    def _get_headers(self) -> dict:
        """获取请求头"""
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/octet-stream"
        }
    
    def upload_file(self, key: str, file_obj: BinaryIO) -> bool:
        """上传文件到 Supabase Storage"""
        if not self.is_available():
            return False
        try:
            # 读取文件内容
            file_content = file_obj.read()
            
            # URL编码key中的路径部分（处理中文字符）
            # 将路径分割为目录和文件名，分别编码
            key_parts = key.split('/')
            encoded_parts = [quote(part, safe='') for part in key_parts]
            encoded_key = '/'.join(encoded_parts)
            
            # 上传文件
            upload_url = f"{self.api_url}/object/{self.bucket_name}/{encoded_key}"
            
            with httpx.Client() as client:
                response = client.post(
                    upload_url,
                    content=file_content,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Supabase upload error: {e}")
            import traceback
            print(f"Supabase upload traceback: {traceback.format_exc()}")
            return False
    
    def download_file(self, key: str) -> Optional[bytes]:
        """从 Supabase Storage 下载文件"""
        if not self.is_available():
            return None
        try:
            # URL编码key中的路径部分（处理中文字符）
            key_parts = key.split('/')
            encoded_parts = [quote(part, safe='') for part in key_parts]
            encoded_key = '/'.join(encoded_parts)
            
            download_url = f"{self.api_url}/object/{self.bucket_name}/{encoded_key}"
            
            with httpx.Client() as client:
                response = client.get(
                    download_url,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            print(f"Supabase download error: {e}")
            return None
    
    def file_exists(self, key: str) -> bool:
        """检查文件是否存在"""
        if not self.is_available():
            return False
        try:
            # URL编码key中的路径部分（处理中文字符）
            key_parts = key.split('/')
            encoded_parts = [quote(part, safe='') for part in key_parts]
            encoded_key = '/'.join(encoded_parts)
            
            # 尝试获取文件信息
            info_url = f"{self.api_url}/object/info/{self.bucket_name}/{encoded_key}"
            
            with httpx.Client() as client:
                response = client.get(
                    info_url,
                    headers=self._get_headers(),
                    timeout=10.0
                )
                return response.status_code == 200
        except:
            return False
    
    def delete_file(self, key: str) -> bool:
        """删除文件"""
        if not self.is_available():
            return False
        try:
            # URL编码key中的路径部分（处理中文字符）
            key_parts = key.split('/')
            encoded_parts = [quote(part, safe='') for part in key_parts]
            encoded_key = '/'.join(encoded_parts)
            
            delete_url = f"{self.api_url}/object/{self.bucket_name}/{encoded_key}"
            
            with httpx.Client() as client:
                response = client.delete(
                    delete_url,
                    headers=self._get_headers(),
                    timeout=10.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Supabase delete error: {e}")
            return False


# 全局存储实例
_supabase_storage = None

def get_supabase_storage() -> SupabaseStorage:
    """获取 Supabase 存储实例（单例）"""
    global _supabase_storage
    if _supabase_storage is None:
        _supabase_storage = SupabaseStorage()
    return _supabase_storage

