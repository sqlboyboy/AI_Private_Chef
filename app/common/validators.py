"""
数据验证工具
"""

from app.common.exceptions import ValidationException
from app.common.logger import logger

def validate_message(message: str, max_length: int = 5000) -> str:
    """
    验证消息内容

    Args:
        message: 消息文本
        max_length: 最大长度

    Returns:
        str: 验证后的消息

    Raises:
        ValidationException: 验证失败时抛出
    """
    if not message:
        raise ValidationException("消息不能为空")

    message = message.strip()

    if not message:
        raise ValidationException("消息不能只包含空格")

    if len(message) > max_length:
        raise ValidationException(f"消息长度不能超过 {max_length} 个字符")

    logger.debug(f"✅ 消息验证通过 - 长度: {len(message)}")
    return message

def validate_thread_id(thread_id: str, max_length: int = 100) -> str:
    """
    验证线程 ID

    Args:
        thread_id: 线程 ID
        max_length: 最大长度

    Returns:
        str: 验证后的线程 ID

    Raises:
        ValidationException: 验证失败时抛出
    """
    if not thread_id:
        raise ValidationException("thread_id 不能为空")

    thread_id = thread_id.strip()

    if not thread_id:
        raise ValidationException("thread_id 不能只包含空格")

    if len(thread_id) > max_length:
        raise ValidationException(f"thread_id 长度不能超过 {max_length} 个字符")

    # 验证格式（只允许字母、数字、下划线、中划线）
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', thread_id):
        raise ValidationException("thread_id 只能包含字母、数字、下划线和中划线")

    logger.debug(f"✅ thread_id 验证通过 - {thread_id}")
    return thread_id

def validate_image_url(image_url: str, max_length: int = 2000) -> str:
    """
    验证图片 URL

    Args:
        image_url: 图片 URL
        max_length: 最大长度

    Returns:
        str: 验证后的 URL

    Raises:
        ValidationException: 验证失败时抛出
    """
    if not image_url:
        return None

    image_url = image_url.strip()

    if not image_url:
        return None

    if len(image_url) > max_length:
        raise ValidationException(f"图片 URL 长度不能超过 {max_length} 个字符")

    # 验证 URL 格式
    if not (image_url.startswith('http://') or image_url.startswith('https://')):
        raise ValidationException("图片 URL 必须以 http:// 或 https:// 开头")

    logger.debug(f"✅ 图片 URL 验证通过")
    return image_url
