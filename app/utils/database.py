import redis
import asyncio
from typing import Optional
import logging

# 导入PostgreSQL相关的数据库操作
from .database_postgres import DatabaseManager, UserRepository, DatabaseUtils

logger = logging.getLogger("app")


def get_redis() -> redis.StrictRedis:
    from app import app_config #延迟引入，避免循环引用
    redis_config = app_config.redis_config
    redis_host = redis_config["host"]
    redis_password = redis_config["password"]
    redis_db = redis_config["db"]
    redis_port = redis_config["port"]
    redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password, decode_responses=True)
    return redis_conn

async def init_database():
    """初始化数据库连接"""
    from app import app_config
    postgres_config = app_config.postgres_config
    await DatabaseManager.init_db(postgres_config)

async def close_database():
    """关闭数据库连接"""
    await DatabaseManager.close_db()

async def check_database_health() -> bool:
    """检查数据库健康状态"""
    return await DatabaseUtils.check_connection()

# 导出常用的数据库操作
__all__ = [
    'get_redis',
    'init_database', 
    'close_database',
    'check_database_health',
    'DatabaseManager',
    'UserRepository',
    'DatabaseUtils'
]