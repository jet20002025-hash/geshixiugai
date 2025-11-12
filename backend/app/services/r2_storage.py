"""
Cloudflare R2 存储适配器
用于替代本地文件系统存储
"""
import os
import boto3
from botocore.config import Config
from pathlib import Path
from typing import BinaryIO, Optional
import io


class R2Storage:
    """Cloudflare R2 存储类"""
    
    def __init__(self):
        self.account_id = os.getenv('R2_ACCOUNT_ID')
        self.access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('R2_BUCKET_NAME', 'word-formatter-storage')
        
        # 构建 R2 endpoint URL
        if self.account_id:
            self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        else:
            self.endpoint_url = os.getenv('R2_ENDPOINT')
        
        # 初始化 S3 客户端（R2 兼容 S3 API）
        if self.access_key_id and self.secret_access_key:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                config=Config(signature_version='s3v4', region_name='auto')
            )
        else:
            self.s3_client = None
    
    def is_available(self) -> bool:
        """检查 R2 存储是否可用"""
        return self.s3_client is not None
    
    def upload_file(self, key: str, file_obj: BinaryIO) -> bool:
        """上传文件到 R2"""
        if not self.is_available():
            return False
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, key)
            return True
        except Exception as e:
            print(f"R2 upload error: {e}")
            return False
    
    def download_file(self, key: str) -> Optional[bytes]:
        """从 R2 下载文件"""
        if not self.is_available():
            return None
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            print(f"R2 download error: {e}")
            return None
    
    def file_exists(self, key: str) -> bool:
        """检查文件是否存在"""
        if not self.is_available():
            return False
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except:
            return False
    
    def delete_file(self, key: str) -> bool:
        """删除文件"""
        if not self.is_available():
            return False
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(f"R2 delete error: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """列出文件"""
        if not self.is_available():
            return []
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            print(f"R2 list error: {e}")
            return []


# 全局存储实例
_r2_storage = None

def get_r2_storage() -> R2Storage:
    """获取 R2 存储实例（单例）"""
    global _r2_storage
    if _r2_storage is None:
        _r2_storage = R2Storage()
    return _r2_storage

