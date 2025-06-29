""" 
存储默认的配置文件
"""
from .constant import *
from .env_loader import env_loader


def get_postgres_config():
    """动态获取PostgreSQL配置，始终从环境变量读取"""
    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": env_loader.get_env("POSTGRES_HOST", "localhost"),
                    "port": env_loader.get_env_int("POSTGRES_PORT", 5432),
                    "user": env_loader.get_env("POSTGRES_USER", "postgres"),
                    "password": env_loader.get_env("POSTGRES_PASSWORD", ""),
                    "database": env_loader.get_env("POSTGRES_DATABASE", ""),
                },
            },
        }, 
        "apps": {
            "models": {
                "models": [
                    "app.models.user",
                ],
                "default_connection": "default",
            },
        },
        'use_tz': False,
        'time_zone': 'Asia/Shanghai'       
    }


def get_redis_config():
    """动态获取Redis配置，始终从环境变量读取"""
    return {
        "host": env_loader.get_env("REDIS_HOST", "localhost"),
        "password": env_loader.get_env("REDIS_PASSWORD", ""),
        "db": env_loader.get_env_int("REDIS_DB", 0),
        "port": env_loader.get_env_int("REDIS_PORT", 6379),
        "user_register_code": REDIS_USER_REGISTER_CODE,
        "user_login_code": REDIS_USER_LOGIN_CODE,
        "user_reset_code": REDIS_USER_RESET_CODE
    }


def get_jwt_config():
    """动态获取JWT配置，始终从环境变量读取"""
    return {
        "jwt_secret_key": env_loader.get_env("JWT_SECRET_KEY", "default_secret_key"),
    }


def get_cookie_config():
    """动态获取Cookie配置，始终从环境变量读取"""
    return {
        "cookie_name": env_loader.get_env("COOKIE_NAME", "auth_token"),
        "cookie_max_age": env_loader.get_env_int("COOKIE_MAX_AGE", 30 * 24 * 60 * 60),  # 30天，单位秒
        "cookie_secure": env_loader.get_env_bool("COOKIE_SECURE", False),  # HTTPS环境设为True
        "cookie_httponly": env_loader.get_env_bool("COOKIE_HTTPONLY", True),
        "cookie_samesite": env_loader.get_env("COOKIE_SAMESITE", "lax"),  # lax, strict, none
        "cookie_domain": env_loader.get_env("COOKIE_DOMAIN", None),  # 可以设置域名
        "cookie_path": env_loader.get_env("COOKIE_PATH", "/"),
    }


def get_verification_code_config():
    """动态获取验证码配置，始终从环境变量读取"""
    return {
        "alibaba_cloud_accesskey_id": env_loader.get_env("ALIBABA_CLOUD_ACCESSKEY_ID", ""),
        "alibaba_cloud_accesskey_secret": env_loader.get_env("ALIBABA_CLOUD_ACCESSKEY_SECRET", ""),
        "sign_name": env_loader.get_env("ALIBABA_CLOUD_SIGN_NAME", ""),
    }


# 基础配置（可以保存到JSON文件的非敏感配置）
DEFAULT_CONFIG={
    "user_config":{
        "user_points":{
            "init_points": 0,
            "invite_points": 1000,
        },
    },
}

