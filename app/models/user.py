
import uuid
from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class User(Model):
    """用户基础信息模型"""
    user_id = fields.UUIDField(pk=True, default=uuid.uuid4, index=True, description="用户唯一标识")
    phone = fields.CharField(max_length=20, unique=True, null=True, description="手机号码")
    account = fields.CharField(max_length=100, unique=True, description="账户名")
    username = fields.CharField(max_length=100, description="用户名")
    password = fields.CharField(max_length=255, description="密码哈希")
    points = fields.IntField(default=0, description="积分")
    invitation_code = fields.CharField(max_length=20, unique=True, null=True, description="邀请码")
    
    # 时间戳字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    
    # 状态字段
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_verified = fields.BooleanField(default=False, description="是否验证")
    
    class Meta:
        table = "users"
        indexes = [
            ["phone"],
            ["account"],
            ["created_at"],
            ["is_active", "is_verified"]
        ]
        
    def __str__(self):
        return f"User({self.account})"


class UserProfile(Model):
    """用户详细信息模型"""
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="profile", on_delete=fields.CASCADE)
    
    # 个人信息
    nickname = fields.CharField(max_length=100, null=True, description="昵称")
    email = fields.CharField(max_length=254, null=True, description="邮箱")
    avatar = fields.TextField(null=True, description="头像URL")
    signature = fields.TextField(null=True, description="个人签名")
    
    # 详细信息
    gender = fields.CharField(max_length=10, null=True, description="性别")
    age = fields.IntField(null=True, description="年龄")
    birthday = fields.DateField(null=True, description="生日")
    address = fields.JSONField(null=True, description="地址信息")
    
    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "user_profiles"


class UserVip(Model):
    """用户会员信息模型"""
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="vip_info", on_delete=fields.CASCADE)
    
    vip_level = fields.IntField(default=0, description="会员等级")
    vip_type = fields.CharField(max_length=50, null=True, description="会员类型")
    vip_start_time = fields.DatetimeField(null=True, description="会员开始时间")
    vip_end_time = fields.DatetimeField(null=True, description="会员结束时间")
    
    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "user_vip"
        indexes = [
            ["vip_level"],
            ["vip_end_time"]
        ]


class UserIdentity(Model):
    """用户身份信息模型"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="identities", on_delete=fields.CASCADE)
    
    identity_type = fields.CharField(max_length=50, description="身份类型")
    identity_value = fields.CharField(max_length=255, description="身份值")
    is_verified = fields.BooleanField(default=False, description="是否验证")
    
    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "user_identities"
        unique_together = [["identity_type", "identity_value"]]
        indexes = [
            ["identity_type"],
            ["is_verified"]
        ]