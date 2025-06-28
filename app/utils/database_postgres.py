"""
PostgreSQL数据库操作工具类
"""
import asyncio
from typing import Optional, List, Dict, Any
from tortoise import Tortoise
from tortoise.transactions import in_transaction
import logging

from app.models.user import User, UserProfile, UserVip, UserIdentity

logger = logging.getLogger("app")


class DatabaseManager:
    """数据库管理器"""
    
    @staticmethod
    async def init_db(config: dict):
        """初始化数据库连接"""
        try:
            await Tortoise.init(config=config)
            await Tortoise.generate_schemas()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    @staticmethod
    async def close_db():
        """关闭数据库连接"""
        await Tortoise.close_connections()
        logger.info("数据库连接已关闭")


class UserRepository:
    """用户数据访问层"""
    
    @staticmethod
    async def create_user(user_data: dict) -> User:
        """创建用户"""
        async with in_transaction() as conn:
            user = await User.create(**user_data, using_db=conn)
            # 创建用户档案
            await UserProfile.create(user=user, using_db=conn)
            # 创建VIP信息
            await UserVip.create(user=user, using_db=conn)
            return user
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return await User.get_or_none(user_id=user_id).prefetch_related(
            "profile", "vip_info", "identities"
        )
    
    @staticmethod
    async def get_user_by_account(account: str) -> Optional[User]:
        """根据账户名获取用户"""
        return await User.get_or_none(account=account).prefetch_related(
            "profile", "vip_info", "identities"
        )
    
    @staticmethod
    async def get_user_by_phone(phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return await User.get_or_none(phone=phone).prefetch_related(
            "profile", "vip_info", "identities"
        )
    
    @staticmethod
    async def update_user(user_id: str, update_data: dict) -> bool:
        """更新用户信息"""
        try:
            await User.filter(user_id=user_id).update(**update_data)
            return True
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return False
    
    @staticmethod
    async def update_user_profile(user_id: str, profile_data: dict) -> bool:
        """更新用户档案"""
        try:
            user = await User.get_or_none(user_id=user_id)
            if not user:
                return False
            
            profile = await UserProfile.get_or_none(user=user)
            if profile:
                await UserProfile.filter(user=user).update(**profile_data)
            else:
                await UserProfile.create(user=user, **profile_data)
            return True
        except Exception as e:
            logger.error(f"更新用户档案失败: {e}")
            return False
    
    @staticmethod
    async def update_user_vip(user_id: str, vip_data: dict) -> bool:
        """更新用户VIP信息"""
        try:
            user = await User.get_or_none(user_id=user_id)
            if not user:
                return False
            
            await UserVip.filter(user=user).update(**vip_data)
            return True
        except Exception as e:
            logger.error(f"更新用户VIP信息失败: {e}")
            return False
    
    @staticmethod
    async def add_user_identity(user_id: str, identity_type: str, identity_value: str) -> bool:
        """添加用户身份信息"""
        try:
            user = await User.get_or_none(user_id=user_id)
            if not user:
                return False
            
            await UserIdentity.create(
                user=user,
                identity_type=identity_type,
                identity_value=identity_value
            )
            return True
        except Exception as e:
            logger.error(f"添加用户身份信息失败: {e}")
            return False
    
    @staticmethod
    async def verify_user_identity(user_id: str, identity_type: str) -> bool:
        """验证用户身份"""
        try:
            user = await User.get_or_none(user_id=user_id)
            if not user:
                return False
            
            await UserIdentity.filter(
                user=user, 
                identity_type=identity_type
            ).update(is_verified=True)
            return True
        except Exception as e:
            logger.error(f"验证用户身份失败: {e}")
            return False
    
    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """删除用户（软删除）"""
        try:
            await User.filter(user_id=user_id).update(is_active=False)
            return True
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False
    
    @staticmethod
    async def get_users_by_filters(
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        vip_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """根据条件查询用户列表"""
        try:
            query = User.all()
            
            if is_active is not None:
                query = query.filter(is_active=is_active)
            if is_verified is not None:
                query = query.filter(is_verified=is_verified)
            if vip_level is not None:
                query = query.filter(vip_info__vip_level=vip_level)
            
            # 计算总数
            total = await query.count()
            
            # 分页查询
            offset = (page - 1) * page_size
            users = await query.offset(offset).limit(page_size).prefetch_related(
                "profile", "vip_info", "identities"
            )
            
            return {
                "users": users,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        except Exception as e:
            logger.error(f"查询用户列表失败: {e}")
            return {"users": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
    
    @staticmethod
    async def update_user_points(user_id: str, points_change: int) -> bool:
        """更新用户积分"""
        try:
            async with in_transaction() as conn:
                user = await User.get_or_none(user_id=user_id, using_db=conn)
                if not user:
                    return False
                
                new_points = max(0, user.points + points_change)  # 确保积分不为负
                await User.filter(user_id=user_id).using_db(conn).update(points=new_points)
                return True
        except Exception as e:
            logger.error(f"更新用户积分失败: {e}")
            return False
    
    @staticmethod
    async def get_user_statistics() -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            total_users = await User.all().count()
            active_users = await User.filter(is_active=True).count()
            verified_users = await User.filter(is_verified=True).count()
            vip_users = await User.filter(vip_info__vip_level__gt=0).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "vip_users": vip_users,
                "inactive_users": total_users - active_users,
                "unverified_users": total_users - verified_users
            }
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {e}")
            return {}


class DatabaseUtils:
    """数据库工具类"""
    
    @staticmethod
    async def execute_raw_sql(sql: str, params: Optional[List] = None) -> List[Dict]:
        """执行原生SQL查询"""
        try:
            from tortoise import connections
            conn = connections.get("default")
            result = await conn.execute_query_dict(sql, params or [])
            return result
        except Exception as e:
            logger.error(f"执行SQL失败: {e}")
            return []
    
    @staticmethod
    async def backup_table(table_name: str) -> bool:
        """备份表数据"""
        try:
            backup_sql = f"""
            CREATE TABLE {table_name}_backup AS 
            SELECT * FROM {table_name}
            """
            await DatabaseUtils.execute_raw_sql(backup_sql)
            logger.info(f"表 {table_name} 备份成功")
            return True
        except Exception as e:
            logger.error(f"备份表 {table_name} 失败: {e}")
            return False
    
    @staticmethod
    async def check_connection() -> bool:
        """检查数据库连接状态"""
        try:
            result = await DatabaseUtils.execute_raw_sql("SELECT 1")
            return len(result) > 0
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False
