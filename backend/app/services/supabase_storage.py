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
        
        # 检查URL是否包含占位符或非ASCII字符
        if self.url and ('你的项目ID' in self.url or 'your-project-id' in self.url.lower()):
            print(f"⚠️ SUPABASE_URL包含占位符，请设置正确的环境变量")
            print(f"⚠️ 当前URL: {self.url[:50]}...")
            self.api_url = None
        elif self.url:
            # 检查URL是否包含非ASCII字符
            try:
                self.url.encode('ascii')
                self.api_url = f"{self.url}/storage/v1"
            except UnicodeEncodeError:
                print(f"⚠️ SUPABASE_URL包含非ASCII字符: {self.url[:50]}...")
                print(f"⚠️ 请检查环境变量 SUPABASE_URL 是否正确设置")
                self.api_url = None
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
            # 如果key包含非ASCII字符，尝试使用UTF-8编码后base64编码
            # 但这通常不应该发生，因为Supabase key应该是ASCII
            print(f"⚠️ SUPABASE_KEY包含非ASCII字符，可能导致上传失败")
            print(f"⚠️ Key前10个字符: {repr(self.key[:10])}")
            # 如果key包含非ASCII字符，我们无法在HTTP头中使用它
            # 这种情况下应该返回错误，但为了不中断流程，我们尝试使用原始key
            # 实际上，如果key包含非ASCII字符，Supabase API调用肯定会失败
            ascii_key = self.key
        
        # 确保所有头值都是字符串类型，并且可以编码为ASCII
        headers = {
            "apikey": str(ascii_key),
            "Authorization": f"Bearer {ascii_key}",
            "Content-Type": "application/octet-stream"
        }
        
        # 验证所有头值都可以编码为ASCII
        for header_name, header_value in headers.items():
            try:
                str(header_value).encode('ascii')
            except UnicodeEncodeError as e:
                print(f"❌ HTTP头 '{header_name}' 的值包含非ASCII字符: {repr(header_value[:20])}")
                print(f"❌ 这会导致httpx请求失败。请检查环境变量 SUPABASE_KEY 是否正确设置。")
                raise ValueError(f"HTTP头 '{header_name}' 包含非ASCII字符，无法发送请求") from e
        
        return headers
    
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
            
            # 构建URL路径，确保所有部分都已编码
            path = '/object/' + self.bucket_name + '/' + '/'.join(encoded_parts)
            # 使用urljoin确保URL正确构建
            upload_url_str = urljoin(self.api_url + '/', path.lstrip('/'))
            # 使用httpx.URL解析URL，确保正确编码
            upload_url = httpx.URL(upload_url_str)
            
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
            
            # 构建URL路径
            path = '/object/' + self.bucket_name + '/' + '/'.join(encoded_parts)
            download_url_str = urljoin(self.api_url + '/', path.lstrip('/'))
            download_url = httpx.URL(download_url_str)
            
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
            
            # 构建URL路径
            path = '/object/info/' + self.bucket_name + '/' + '/'.join(encoded_parts)
            info_url_str = urljoin(self.api_url + '/', path.lstrip('/'))
            info_url = httpx.URL(info_url_str)
            
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
            
            # 构建URL路径
            path = '/object/' + self.bucket_name + '/' + '/'.join(encoded_parts)
            delete_url_str = urljoin(self.api_url + '/', path.lstrip('/'))
            delete_url = httpx.URL(delete_url_str)
            
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

