"""
schemas/user.py
用户相关的数据模型
"""

from pydantic import  UUID4, EmailStr, constr
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator




class UserRegister(BaseModel):
    username: Optional[str] = Field(
        default=None,
        description="用户的用户名，可选"
    )
    phone: str = Field(
        ...,
        description="用户的手机号码或者账号必填",
        min_length=11,
        max_length=11
    )
    password: str = Field(
        ...,
        description="用户的密码，必填",
        min_length=6,
        max_length=20
    )
    verification_code: Optional[str]= Field(
        default=None,
        description="验证码，可选",
        min_length=4,
        max_length=6
    )
    invitation_code: Optional[str] = Field(
        default=None,
        description="邀请码，可选"
    )

    @field_validator('phone')
    def validate_phone(cls, value):
        if not value.isdigit():
            raise ValueError("手机号码必须为数字")
        return value


class UserLogin(BaseModel): 
    phone: str = Field(
        ...,
        description="用户的手机号码或者账号，必填",
        min_length=11,
        max_length=11
    )
    password: Optional[str] = Field(
        default=None,
        description="用户的密码，可选",
        min_length=6,
        max_length=20
    )
    verification_code: Optional[str] = Field(
        default=None,
        description="验证码，可选",
        min_length=4,
        max_length=6
    )

    @field_validator('phone')
    def validate_phone(cls, value):
        if not value.isdigit():
            raise ValueError("手机号码必须为数字")
        return value


class UserReset(BaseModel):
    username: Optional[str] = Field(
        default=None,
        description="用户的用户名，可选，可以修改"
    )
    phone: str = Field(
        ...,
        description="用户的手机号码或者账号，必填",
        min_length=11,
        max_length=11
    )
    old_password: Optional[str] = Field(
        ...,
        description="用户的密码，选填",
        min_length=6,
        max_length=20
    )
    new_password: Optional[str] = Field(
        ...,
        description="用户的新密码，选填",
        min_length=6,
        max_length=20
    )
    verification_code:Optional[str] = Field(
        ...,
        description="验证码，选填",
        min_length=4,
        max_length=6
    )
    account: Optional[str] = Field(
        default=None,
        description="用户的账号，可选",
        min_length=11,
        max_length=11
    )
    invitation_code: Optional[str] = Field(
        default=None,
        description="邀请码，可选"
    )

    @field_validator('phone')
    def validate_phone(cls, value):
        if not value.isdigit():
            raise ValueError("手机号码必须为数字")
        return value


class UserProfileResponse(BaseModel):
    """用户个人信息响应模型"""
    user_id: str = Field(..., description="用户ID")
    account: str = Field(..., description="账户名")
    username: str = Field(..., description="用户名")
    phone: Optional[str] = Field(None, description="手机号码")
    points: int = Field(0, description="用户积分")
    invitation_code: Optional[str] = Field(None, description="邀请码")
    is_active: bool = Field(True, description="是否激活")
    is_verified: bool = Field(False, description="是否验证")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    last_login: Optional[str] = Field(None, description="最后登录时间")
    
    # 扩展信息
    profile: Optional[dict] = Field(None, description="详细资料")
    vip_info: Optional[dict] = Field(None, description="会员信息")


class UserProfileUpdateRequest(BaseModel):
    """用户信息更新请求模型"""
    username: Optional[str] = Field(None, description="用户名", max_length=100)
    nickname: Optional[str] = Field(None, description="昵称", max_length=100)
    email: Optional[EmailStr] = Field(None, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像URL")
    signature: Optional[str] = Field(None, description="个人签名")
    gender: Optional[str] = Field(None, description="性别", max_length=10)
    age: Optional[int] = Field(None, description="年龄", ge=1, le=150)
    address: Optional[dict] = Field(None, description="地址信息")







