import os
import base64
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import OSSUploadResponse, OSSSignature
from app.common.logger import logger
import requests

router = APIRouter()

# ============================================================
# OSS 配置
# ============================================================
def get_oss_config():
    """获取 OSS 配置（在运行时读取，以支持 .env 文件加载）"""
    return {
        'access_key_id': os.getenv("OSS_ACCESS_KEY_ID"),
        'access_key_secret': os.getenv("OSS_ACCESS_KEY_SECRET"),
        'bucket_name': os.getenv("OSS_BUCKET_NAME", "personal-chief"),
        'endpoint': os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com"),
        'upload_dir': os.getenv("OSS_UPLOAD_DIR", "uploads/")
    }

# 为了向后兼容，保留这些变量
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME", "personal-chief")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_UPLOAD_DIR = os.getenv("OSS_UPLOAD_DIR", "uploads/")

# ============================================================
# 验证 OSS 配置
# ============================================================
def validate_oss_config():
    """验证 OSS 配置是否完整"""
    config = get_oss_config()
    if not config['access_key_id'] or not config['access_key_secret']:
        logger.warning("⚠️ OSS 配置不完整，将使用模拟签名")
        return False
    return True

# ============================================================
# 生成 OSS 签名
# ============================================================
def generate_oss_signature():
    """
    生成阿里云 OSS 上传签名

    Returns:
        dict: 包含签名信息的字典
    """
    try:
        config = get_oss_config()

        # 检查配置
        if not validate_oss_config():
            logger.info("📝 使用模拟 OSS 签名")
            return generate_mock_signature()

        # 生成过期时间（1小时后）
        expiration = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'

        # 构建 Policy
        policy_dict = {
            "expiration": expiration,
            "conditions": [
                ["content-length-range", 0, 104857600],  # 100MB
                ["starts-with", "$key", config['upload_dir']],
                ["eq", "$bucket", config['bucket_name']]
            ]
        }

        # 编码 Policy
        policy_str = json.dumps(policy_dict)
        policy_b64 = base64.b64encode(policy_str.encode('utf-8')).decode('utf-8')

        # 生成签名
        import hmac
        import hashlib
        signature = base64.b64encode(
            hmac.new(
                config['access_key_secret'].encode('utf-8'),
                policy_b64.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')

        logger.info("✅ OSS 签名生成成功")

        return {
            "accessKeyId": config['access_key_id'],
            "policy": policy_b64,
            "signature": signature,
            "dir": config['upload_dir'],
            "host": f"https://{config['bucket_name']}.{config['endpoint']}",
            "expiration": expiration
        }

    except Exception as e:
        logger.error(f"❌ OSS 签名生成失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="签名生成失败，请稍后重试"
        )

def generate_mock_signature():
    """生成模拟签名（用于开发测试）"""
    config = get_oss_config()
    expiration = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
    return {
        "accessKeyId": "mock-access-key-id",
        "policy": "mock-policy",
        "signature": "mock-signature",
        "dir": config['upload_dir'],
        "host": f"https://{config['bucket_name']}.{config['endpoint']}",
        "expiration": expiration
    }

# ============================================================
# API 端点
# ============================================================

@router.post("/upload-signature", response_model=OSSUploadResponse)
async def get_upload_signature():
    """
    获取 OSS 上传签名

    Returns:
        OSSUploadResponse: 包含签名信息的响应

    Raises:
        HTTPException: 签名生成失败时返回 500 错误
    """
    try:
        logger.info("📤 请求 OSS 上传签名")

        # 生成签名
        signature_data = generate_oss_signature()

        # 构建响应
        response = OSSUploadResponse(
            status="success",
            signature=OSSSignature(**signature_data),
            message="签名生成成功"
        )

        logger.info("✅ OSS 上传签名返回成功")
        return response

    except Exception as e:
        logger.error(f"❌ 获取 OSS 签名失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取上传签名失败，请稍后重试"
        )

@router.get("/test")
async def oss_test():
    """OSS API 测试端点"""
    config = get_oss_config()
    logger.info("🧪 OSS API 测试")
    return {
        "message": "OSS API is working",
        "status": "ok",
        "config": {
            "bucket": config['bucket_name'],
            "endpoint": config['endpoint'],
            "upload_dir": config['upload_dir'],
            "has_credentials": bool(config['access_key_id'] and config['access_key_secret'])
        }
    }

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件到 OSS（后端代理）

    Args:
        file: 上传的文件

    Returns:
        dict: 包含文件 URL 的响应

    Raises:
        HTTPException: 上传失败时返回错误
    """
    try:
        logger.info(f"📤 开始上传文件: {file.filename}")

        # 获取上传签名（如果配置不完整会使用模拟签名）
        logger.info("📝 生成上传签名...")
        signature_data = generate_oss_signature()

        # 读取文件内容
        file_content = await file.read()

        # 生成文件名
        file_key = f"{signature_data['dir']}{datetime.now().timestamp()}_{file.filename}"

        # 如果使用模拟签名，直接返回模拟 URL
        if signature_data['signature'] == 'mock-signature':
            logger.info("📝 使用模拟签名，返回模拟 URL")
            file_url = f"{signature_data['host']}/{file_key}"
            return {
                "status": "success",
                "file_url": file_url,
                "file_name": file.filename,
                "file_size": len(file_content)
            }

        # 准备上传数据
        files = {
            'key': (None, file_key),
            'policy': (None, signature_data['policy']),
            'OSSAccessKeyId': (None, signature_data['accessKeyId']),
            'signature': (None, signature_data['signature']),
            'file': (file.filename, file_content, file.content_type)
        }

        # 上传到 OSS
        logger.info(f"📤 上传到 OSS: {signature_data['host']}")
        response = requests.post(signature_data['host'], files=files)

        if response.status_code not in [200, 204]:
            logger.error(f"❌ OSS 上传失败: {response.status_code}")
            raise HTTPException(
                status_code=500,
                detail=f"OSS 上传失败: {response.status_code}"
            )

        # 构建文件 URL
        file_url = f"{signature_data['host']}/{file_key}"

        logger.info(f"✅ 文件上传成功: {file_url}")

        return {
            "status": "success",
            "file_url": file_url,
            "file_name": file.filename,
            "file_size": len(file_content)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 文件上传失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="文件上传失败，请稍后重试"
        )