from typing import Optional, List

from pydantic import BaseModel

# --- 对话相关模型 ---
class ChatRequest(BaseModel):
    message: str
    image_url: Optional[str] = None
    thread_id: str

# --- OSS 相关模型 ---
class OSSSignature(BaseModel):
    """OSS 上传签名响应"""
    accessKeyId: str
    policy: str
    signature: str
    dir: str
    host: str
    expiration: str

class OSSUploadResponse(BaseModel):
    """OSS 上传响应"""
    status: str
    signature: OSSSignature
    message: Optional[str] = None