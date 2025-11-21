"""
Backblaze B2 Storage 存储适配器
使用 S3 兼容 API
"""
import os
import boto3
from botocore.config import Config
from typing import BinaryIO, Optional
from .storage_base import StorageBase


class B2Storage(StorageBase):
    """Backblaze B2 存储类（S3 兼容）"""
    
    def __init__(self):
        self.account_id = os.getenv('B2_ACCOUNT_ID')
        self.application_key = os.getenv('B2_APPLICATION_KEY')
        self.bucket_name = os.getenv('B2_BUCKET_NAME', 'word-formatter-storage')
        self.endpoint_url = os.getenv('B2_ENDPOINT', '')
        
        # 初始化 S3 客户端（B2 兼容 S3 API）
        if self.account_id and self.application_key and self.endpoint_url:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.account_id,
                aws_secret_access_key=self.application_key,
                config=Config(signature_version='s3v4')
            )
        else:
            self.s3_client = None
    
    def is_available(self) -> bool:
        """检查 B2 存储是否可用"""
        return self.s3_client is not None
    
    def upload_file(self, key: str, file_obj: BinaryIO) -> bool:
        """上传文件到 B2"""
        if not self.is_available():
            return False
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, key)
            return True
        except Exception as e:
            print(f"B2 upload error: {e}")
            return False
    
    def download_file(self, key: str) -> Optional[bytes]:
        """从 B2 下载文件"""
        if not self.is_available():
            return None
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            print(f"B2 download error: {e}")
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
            print(f"B2 delete error: {e}")
            return False
    
    def get_presigned_upload_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """获取预签名上传URL（用于前端直接上传）"""
        if not self.is_available():
            return None
        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"B2 presigned URL error: {e}")
            return None


# 全局存储实例
_b2_storage = None

def get_b2_storage() -> B2Storage:
    """获取 B2 存储实例（单例）"""
    global _b2_storage
    if _b2_storage is None:
        _b2_storage = B2Storage()
    return _b2_storage

