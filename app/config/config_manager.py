"""
配置管理工具
用于管理配置文件的创建、验证和更新
"""
import os
import json
import shutil
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.env_file = os.path.join(self.base_dir, ".env")
        self.env_example = os.path.join(self.base_dir, ".env.example")
        self.config_file = os.path.join(self.base_dir, "data", "config.json")
        self.config_example = os.path.join(self.base_dir, "config.json.example")
    
    def init_config_files(self):
        """初始化配置文件"""
        print("正在初始化配置文件...")
        
        # 创建data目录
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # 复制.env文件
        if not os.path.exists(self.env_file) and os.path.exists(self.env_example):
            shutil.copy2(self.env_example, self.env_file)
            print(f"已创建 .env 文件，请编辑 {self.env_file} 并填入正确的配置信息")
        
        # 复制config.json文件
        if not os.path.exists(self.config_file) and os.path.exists(self.config_example):
            shutil.copy2(self.config_example, self.config_file)
            print(f"已创建配置文件 {self.config_file}")
        
        print("配置文件初始化完成！")
    
    def validate_env_file(self) -> bool:
        """验证.env文件是否包含所有必需的环境变量"""
        required_vars = [
            "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DATABASE",
            "REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD", "REDIS_DB",
            "JWT_SECRET_KEY",
            "ALIBABA_CLOUD_ACCESSKEY_ID", "ALIBABA_CLOUD_ACCESSKEY_SECRET", "ALIBABA_CLOUD_SIGN_NAME"
        ]
        
        if not os.path.exists(self.env_file):
            print(f"错误：.env 文件不存在: {self.env_file}")
            return False
        
        missing_vars = []
        with open(self.env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for var in required_vars:
                if f"{var}=" not in content:
                    missing_vars.append(var)
        
        if missing_vars:
            print(f"错误：.env 文件缺少以下环境变量: {', '.join(missing_vars)}")
            return False
        
        print(".env 文件验证通过")
        return True
    
    def validate_config_file(self) -> bool:
        """验证config.json文件格式是否正确"""
        if not os.path.exists(self.config_file):
            print(f"错误：配置文件不存在: {self.config_file}")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                json.load(f)
            print("config.json 文件验证通过")
            return True
        except json.JSONDecodeError as e:
            print(f"错误：配置文件格式错误: {e}")
            return False
    
    def show_config_status(self):
        """显示配置文件状态"""
        print("=== 配置文件状态 ===")
        
        files_to_check = [
            (".env", self.env_file),
            ("config.json", self.config_file),
            (".env.example", self.env_example),
            ("config.json.example", self.config_example)
        ]
        
        for name, path in files_to_check:
            status = "✓ 存在" if os.path.exists(path) else "✗ 不存在"
            print(f"{name}: {status}")
        
        print("\n=== 验证结果 ===")
        self.validate_env_file()
        self.validate_config_file()


def main():
    """主函数"""
    manager = ConfigManager()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "init":
            manager.init_config_files()
        elif command == "check":
            manager.show_config_status()
        elif command == "validate":
            env_valid = manager.validate_env_file()
            config_valid = manager.validate_config_file()
            if env_valid and config_valid:
                print("所有配置文件验证通过！")
            else:
                print("配置文件验证失败！")
                sys.exit(1)
        else:
            print("可用命令: init, check, validate")
    else:
        manager.show_config_status()


if __name__ == "__main__":
    main()
