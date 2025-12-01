"""
阿里云 OSS 存储适配器
使用 S3 兼容 API
"""
import os
import boto3
from botocore.config import Config
from typing import BinaryIO, Optional
from .storage_base import StorageBase


class OSSStorage(StorageBase):
    """阿里云 OSS 存储类（S3 兼容）"""
    
    def __init__(self):
        self.access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
        self.bucket_name = os.getenv('OSS_BUCKET_NAME', 'word-formatter-storage')
        self.endpoint = os.getenv('OSS_ENDPOINT', '')
        self.region = os.getenv('OSS_REGION', 'cn-hangzhou')
        
        # 如果没有指定 endpoint，根据 region 自动构建
        if not self.endpoint and self.region:
            self.endpoint = f"https://oss-{self.region}.aliyuncs.com"
        
        # 初始化 S3 客户端（OSS 兼容 S3 API）
        if self.access_key_id and self.access_key_secret and self.endpoint:
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=self.endpoint,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.access_key_secret,
                    config=Config(signature_version='s3v4', region_name=self.region)
                )
            except Exception as e:
                print(f"OSS client initialization error: {e}")
                self.s3_client = None
        else:
            self.s3_client = None
    
    def is_available(self) -> bool:
        """检查 OSS 存储是否可用"""
        return self.s3_client is not None
    
    def upload_file(self, key: str, file_obj: BinaryIO) -> bool:
        """上传文件到 OSS"""
        if not self.is_available():
            return False
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, key)
            return True
        except Exception as e:
            print(f"OSS upload error: {e}")
            return False
    
    def download_file(self, key: str) -> Optional[bytes]:
        """从 OSS 下载文件"""
        if not self.is_available():
            return None
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            print(f"OSS download error: {e}")
            return None
    
    def file_exists(self, key: str) -> bool:
        """检查文件是否存在"""
        if not self.is_available():
            return False
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            if '404' in str(e) or 'NoSuchKey' in str(e):
                return False
            print(f"OSS file_exists error: {e}")
            return False
    
    def delete_file(self, key: str) -> bool:
        """删除文件"""
        if not self.is_available():
            return False
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(f"OSS delete error: {e}")
            return False
    
    def get_file_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """获取文件的临时访问 URL"""
        if not self.is_available():
            return None
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"OSS get_file_url error: {e}")
            return None


def get_oss_storage() -> OSSStorage:
    """获取 OSS 存储实例"""
    return OSSStorage()

