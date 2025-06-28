"""
环境变量加载器
从 .env 文件中加载环境变量
"""
import os
from typing import Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


class EnvLoader:
    """环境变量加载器"""
    
    def __init__(self, env_file: str = ".env"):
        # 获取项目根目录（main.py 所在的目录）
        project_root = Path(__file__).parent.parent.parent
        self.env_file = project_root / env_file
        self.load_env()
    
    def load_env(self):
        """加载环境变量"""
        if HAS_DOTENV:
            # 使用 python-dotenv 加载，override=True 确保覆盖已存在的环境变量
            load_dotenv(self.env_file, override=True)
        else:
            # 手动加载
            self._manual_load_env()
    
    def _manual_load_env(self):
        """手动加载环境变量"""
        if not os.path.exists(self.env_file):
            return
        
        with open(self.env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
    
    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量"""
        return os.environ.get(key, default)
    
    @staticmethod
    def get_env_int(key: str, default: int = 0) -> int:
        """获取环境变量并转换为整数"""
        value = os.environ.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    @staticmethod
    def get_env_bool(key: str, default: bool = False) -> bool:
        """获取环境变量并转换为布尔值"""
        value = os.environ.get(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')


# 创建全局实例
env_loader = EnvLoader()
