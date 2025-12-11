"""
Supabase Storage 存储适配器
用于替代本地文件系统存储
"""
import os
import httpx
from urllib.parse import quote, urljoin
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
        # 确保所有头值都是ASCII或已正确编码的字符串
        # 如果key包含非ASCII字符，httpx会尝试编码为ASCII并失败
        # 所以我们需要确保key是纯ASCII
        try:
            # 尝试将key编码为ASCII，如果失败则说明key本身有问题
            ascii_key = self.key.encode('ascii').decode('ascii')
        except UnicodeEncodeError:
            # 如果key包含非ASCII字符，记录错误但不使用
            print(f"⚠️ SUPABASE_KEY包含非ASCII字符，可能导致上传失败")
            ascii_key = self.key
        
        return {
            "apikey": ascii_key,
            "Authorization": f"Bearer {ascii_key}",
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
            
            # 使用httpx.URL直接构建URL，确保正确编码
            # 这样可以避免字符串拼接导致的编码问题
            base_url = httpx.URL(self.api_url)
            path_segments = ['object', self.bucket_name] + encoded_parts
            upload_url = base_url.copy_with(path='/'.join([''] + path_segments))
            
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
            # 打印调试信息
            print(f"Debug: key={key}, encoded_key={encoded_key if 'encoded_key' in locals() else 'N/A'}")
            print(f"Debug: api_url={self.api_url}, bucket_name={self.bucket_name}")
            return False
    
    def download_file(self, key: str) -> Optional[bytes]:
        """从 Supabase Storage 下载文件"""
        if not self.is_available():
            return None
        try:
            # URL编码key中的路径部分（处理中文字符）
            key_parts = key.split('/')
            encoded_parts = [quote(part, safe='') for part in key_parts]
            
            # 使用httpx.URL直接构建URL
            base_url = httpx.URL(self.api_url)
            path_segments = ['object', self.bucket_name] + encoded_parts
            download_url = base_url.copy_with(path='/'.join([''] + path_segments))
            
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
            
            # 使用httpx.URL直接构建URL
            base_url = httpx.URL(self.api_url)
            path_segments = ['object', 'info', self.bucket_name] + encoded_parts
            info_url = base_url.copy_with(path='/'.join([''] + path_segments))
            
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
            
            # 使用httpx.URL直接构建URL
            base_url = httpx.URL(self.api_url)
            path_segments = ['object', self.bucket_name] + encoded_parts
            delete_url = base_url.copy_with(path='/'.join([''] + path_segments))
            
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

