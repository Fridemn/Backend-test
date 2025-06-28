# web 服务器
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import os

from app import logger, app_config
from app.api.user import api_user
from app.api.system import api_system

#from wordease.api.user import api_user

logo_tmpl=r"""
----------------------------------------
            app已经运行
----------------------------------------
"""


def check_env():
    os.makedirs("data/", exist_ok=True)

def create_app():
    """创建FastAPI应用并配置数据库"""
    app = FastAPI(
        title="API模板",
        description="后端API模板项目",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 获取PostgreSQL配置并打印调试信息
    postgres_config = app_config.postgres_config
    credentials = postgres_config['connections']['default']['credentials']
    logger.info(f"数据库配置: {credentials['host']}:{credentials['port']}/{credentials['database']}")
    
    # 初始化 Tortoise ORM
    register_tortoise(
        app,
        config=postgres_config,
        generate_schemas=True,  # 开发环境可以生成表结构，生产环境建议关闭
        add_exception_handlers=True,  # 显示错误信息
    )
    
    # 添加根路由
    @app.get("/", summary="根路径", description="API健康检查接口")
    async def root():
        return {"message": "欢迎使用API模板", "status": "running", "version": "0.1.0"}
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有方法
        allow_headers=["*"],  # 允许所有头
    )
    
    # 注册路由
    app.include_router(api_user, prefix="/user", tags=["用户相关接口"])
    app.include_router(api_system, prefix="/system", tags=["系统相关接口"])
    
    return app

check_env()

app = create_app()


if __name__ == '__main__':
    logger.info(logo_tmpl)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    