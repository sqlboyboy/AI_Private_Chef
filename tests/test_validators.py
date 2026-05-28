"""
单元测试 - 数据验证
"""

import pytest
from app.common.validators import validate_message, validate_thread_id, validate_image_url
from app.common.exceptions import ValidationException

class TestValidators:
    """验证器测试类"""

    # ============================================================
    # 消息验证测试
    # ============================================================
    def test_validate_message_success(self):
        """测试有效消息"""
        result = validate_message("你好，我有番茄和鸡蛋")
        assert result == "你好，我有番茄和鸡蛋"

    def test_validate_message_empty(self):
        """测试空消息"""
        with pytest.raises(ValidationException):
            validate_message("")

    def test_validate_message_whitespace_only(self):
        """测试只包含空格的消息"""
        with pytest.raises(ValidationException):
            validate_message("   ")

    def test_validate_message_too_long(self):
        """测试过长的消息"""
        long_message = "a" * 5001
        with pytest.raises(ValidationException):
            validate_message(long_message)

    def test_validate_message_strip_whitespace(self):
        """测试消息去除前后空格"""
        result = validate_message("  你好  ")
        assert result == "你好"

    # ============================================================
    # 线程 ID 验证测试
    # ============================================================
    def test_validate_thread_id_success(self):
        """测试有效的 thread_id"""
        result = validate_thread_id("user-001")
        assert result == "user-001"

    def test_validate_thread_id_empty(self):
        """测试空 thread_id"""
        with pytest.raises(ValidationException):
            validate_thread_id("")

    def test_validate_thread_id_whitespace_only(self):
        """测试只包含空格的 thread_id"""
        with pytest.raises(ValidationException):
            validate_thread_id("   ")

    def test_validate_thread_id_invalid_chars(self):
        """测试包含无效字符的 thread_id"""
        with pytest.raises(ValidationException):
            validate_thread_id("user@001")

    def test_validate_thread_id_too_long(self):
        """测试过长的 thread_id"""
        long_id = "a" * 101
        with pytest.raises(ValidationException):
            validate_thread_id(long_id)

    def test_validate_thread_id_valid_formats(self):
        """测试各种有效格式的 thread_id"""
        valid_ids = [
            "user-001",
            "user_001",
            "user001",
            "USER001",
            "user-001_test"
        ]
        for thread_id in valid_ids:
            result = validate_thread_id(thread_id)
            assert result == thread_id

    # ============================================================
    # 图片 URL 验证测试
    # ============================================================
    def test_validate_image_url_success(self):
        """测试有效的图片 URL"""
        url = "https://example.com/image.jpg"
        result = validate_image_url(url)
        assert result == url

    def test_validate_image_url_http(self):
        """测试 HTTP 图片 URL"""
        url = "http://example.com/image.jpg"
        result = validate_image_url(url)
        assert result == url

    def test_validate_image_url_empty(self):
        """测试空 URL"""
        result = validate_image_url("")
        assert result is None

    def test_validate_image_url_none(self):
        """测试 None URL"""
        result = validate_image_url(None)
        assert result is None

    def test_validate_image_url_invalid_protocol(self):
        """测试无效协议的 URL"""
        with pytest.raises(ValidationException):
            validate_image_url("ftp://example.com/image.jpg")

    def test_validate_image_url_too_long(self):
        """测试过长的 URL"""
        long_url = "https://example.com/" + "a" * 2000
        with pytest.raises(ValidationException):
            validate_image_url(long_url)

    def test_validate_image_url_strip_whitespace(self):
        """测试 URL 去除前后空格"""
        url = "  https://example.com/image.jpg  "
        result = validate_image_url(url)
        assert result == "https://example.com/image.jpg"
