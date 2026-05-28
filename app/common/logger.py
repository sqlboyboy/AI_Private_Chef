import logging
import sys
import os
from datetime import datetime

# ============================================================
# 日志配置
# ============================================================

# 日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_FORMAT_DETAILED = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"

# 日志文件配置
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# ============================================================
# 创建日志目录
# ============================================================
def ensure_log_dir():
    """确保日志目录存在"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"✅ 创建日志目录: {LOG_DIR}")

# ============================================================
# 设置日志
# ============================================================
def setup_logging():
    """
    配置日志系统

    配置包括：
    - 控制台输出（INFO 级别）
    - 文件输出（DEBUG 级别，更详细）
    - 日志格式和时间戳
    """
    ensure_log_dir()

    # 获取根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))

    # 清除已有的处理器
    root_logger.handlers.clear()

    # ============================================================
    # 控制台处理器（INFO 级别）
    # ============================================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # ============================================================
    # 文件处理器（DEBUG 级别，更详细）
    # ============================================================
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT_DETAILED)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        print(f"✅ 日志文件: {LOG_FILE}")
    except Exception as e:
        print(f"⚠️ 无法创建日志文件: {e}")

# ============================================================
# 创建全局 logger 实例
# ============================================================
logger = logging.getLogger("personal_chief")

# ============================================================
# 日志工具函数
# ============================================================
def log_request(method: str, path: str, params: dict = None):
    """记录 API 请求"""
    params_str = f" - 参数: {params}" if params else ""
    logger.info(f"📨 {method} {path}{params_str}")

def log_response(status_code: int, message: str = ""):
    """记录 API 响应"""
    emoji = "✅" if 200 <= status_code < 300 else "❌"
    logger.info(f"{emoji} 响应状态: {status_code} {message}")

def log_error(error_type: str, error_message: str, exc_info=False):
    """记录错误"""
    logger.error(f"❌ {error_type}: {error_message}", exc_info=exc_info)