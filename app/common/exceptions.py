"""
自定义异常类
"""

class PersonalChiefException(Exception):
    """基础异常类"""
    pass

class AgentException(PersonalChiefException):
    """Agent 相关异常"""
    pass

class OSSException(PersonalChiefException):
    """OSS 相关异常"""
    pass

class ValidationException(PersonalChiefException):
    """数据验证异常"""
    pass

class ConfigException(PersonalChiefException):
    """配置异常"""
    pass
