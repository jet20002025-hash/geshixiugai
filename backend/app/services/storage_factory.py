"""
存储工厂类
根据环境变量自动选择可用的存储后端
"""
import os
from typing import Optional
from .storage_base import StorageBase
from .r2_storage import get_r2_storage
from .supabase_storage import get_supabase_storage
from .b2_storage import get_b2_storage


def get_storage() -> Optional[StorageBase]:
    """
    获取可用的存储实例
    按优先级顺序检查：Supabase > B2 > R2
    
    Returns:
        可用的存储实例，如果都不可用则返回 None
    """
    # 优先级 1: Supabase Storage
    supabase = get_supabase_storage()
    if supabase.is_available():
        print("[Storage] Using Supabase Storage")
        return supabase
    
    # 优先级 2: Backblaze B2
    b2 = get_b2_storage()
    if b2.is_available():
        print("[Storage] Using Backblaze B2 Storage")
        return b2
    
    # 优先级 3: Cloudflare R2
    r2 = get_r2_storage()
    if r2.is_available():
        print("[Storage] Using Cloudflare R2 Storage")
        return r2
    
    # 所有存储都不可用
    print("[Storage] No storage backend available")
    return None

