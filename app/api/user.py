"""
user.py
存放用户相关接口，如登录注册修改信息等
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q
from datetime import datetime
import uuid
from datetime import datetime

from app.config.constant import *
from app import redis_client, app_config, logger
from app.models.user import User, UserProfile, UserVip
from app.schemas.response import ResponseModel
from app.schemas.user import UserRegister, UserLogin, UserReset, UserProfileUpdateRequest, UserProfileUpdateRequest
from app.utils.user import create_jwt, get_current_user, get_code, check_code, generate_account, md5, get_current_user_from_request, get_token_from_request, decode_jwt, get_user_from_token, get_user_from_request_without_blacklist
from app.utils.database_postgres import UserRepository


async def get_user_by_phone(phone: str) -> User:
    """根据手机号获取用户"""
    return await UserRepository.get_user_by_phone(phone)


def set_auth_cookie(response: Response, token: str):
    """设置认证cookie"""
    cookie_config = app_config.cookie_config
    response.set_cookie(
        key=cookie_config["cookie_name"],
        value=token,
        max_age=cookie_config["cookie_max_age"],
        httponly=cookie_config["cookie_httponly"],
        secure=cookie_config["cookie_secure"],
        samesite=cookie_config["cookie_samesite"],
        domain=cookie_config["cookie_domain"],
        path=cookie_config["cookie_path"]
    )


def clear_auth_cookie(response: Response):
    """清除认证cookie"""
    cookie_config = app_config.cookie_config
    response.delete_cookie(
        key=cookie_config["cookie_name"],
        domain=cookie_config["cookie_domain"],
        path=cookie_config["cookie_path"]
    )


api_user = APIRouter()



#------------------------------
#用户注册部分,有两种注册方式，一种是手机号+密码，一种是手机号+验证码
#------------------------------

@api_user.get("/register/verification-code/send",description="发送注册验证码，必填手机号")
async def register_verification_code_get(phone : str):
    REDIS_USER_REGISTER_CODE = app_config.redis_config["user_register_code"]
    await get_code(phone, REDIS_USER_REGISTER_CODE)
    return ResponseModel.success("注册账号验证码发送成功")


@api_user.post("/register/verification-code-way", description="通过验证码的方式进行用户注册，验证刚刚发送的注册验证码，邀请码选填")
async def register_by_verification_code(user_register: UserRegister, response: Response):
    username = user_register.username
    phone = user_register.phone
    password = user_register.password
    verification_code = user_register.verification_code
    invitation_code = user_register.invitation_code

    user_config = app_config["user_config"]
    init_points = user_config["user_points"]["init_points"]
    add_points = user_config["user_points"]["invite_points"]

    if not username:
        username = "用户" + str(phone)
    
    REDIS_USER_REGISTER_CODE = app_config.redis_config["user_register_code"]
    
    if verification_code:
        await check_code(verification_code, phone, REDIS_USER_REGISTER_CODE)
    
    # 使用新的数据库操作方法
    user = await UserRepository.get_user_by_phone(phone)

    if user:
        token = create_jwt(user)
        set_auth_cookie(response, token)  # 设置cookie
        return ResponseModel.success("用户已存在，已登录", {"current_user": get_user_from_token(token), "token": token})
    else:
        # 用户不存在，创建新用户并直接登录
        new_user_points = init_points
        
        # 处理邀请码逻辑
        if invitation_code:
            inviting_user = await User.filter(invitation_code=invitation_code).first()
            if inviting_user:
                # 更新邀请者积分
                await UserRepository.update_user_points(str(inviting_user.user_id), add_points)
                new_user_points += add_points
        
        # 创建新用户
        try:
            user_data = {
                "account": phone,
                "phone": phone,
                "username": username,
                "password": md5(password),
                "points": new_user_points,
                "invitation_code": str(uuid.uuid4())[:8]  # 生成邀请码
            }
            new_user = await UserRepository.create_user(user_data)
            token = create_jwt(new_user)
            set_auth_cookie(response, token)  # 设置cookie
            return ResponseModel.success("注册用户成功", {"current_user": get_user_from_token(token), "token": token})
        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            raise HTTPException(status_code=500, detail="用户创建失败，请稍后重试")
        

@api_user.post("/register/password-way",description="通过密码的方式进行用户注册，邀请码选填")
async def register_by_password(user_register: UserRegister, response: Response):
    username = user_register.username
    phone = user_register.phone
    password = user_register.password
    invitation_code = user_register.invitation_code

    user_config=app_config["user_config"]
    init_points = user_config["user_points"]["init_points"]
    add_points = user_config["user_points"]["invite_points"]

    if not username:
        username = "用户" + str(phone)
    user = await User.filter(phone = phone).first()
    if user:
        token = create_jwt(user)
        set_auth_cookie(response, token)  # 设置cookie
        return ResponseModel.success("用户已存在，已登录", {"current_user" : get_user_from_token(token), "token" : token})
    else:
        # 用户不存在，创建新用户并直接登录,两者邀请加积分
        inviting_user = await User.filter(invitation_code=invitation_code).first()
        if inviting_user:
            inviting_user_old_points = inviting_user.points
            inviting_user.points=add_points + inviting_user_old_points
            await inviting_user.save()
        new_user_points = add_points+init_points
        # 新建用户
        try:
            newUser = await User.create(
                account = phone,
                phone = phone,
                username = username,
                password = md5(password),
                points = new_user_points
            )
            token = create_jwt(newUser)
            set_auth_cookie(response, token)  # 设置cookie
            return ResponseModel.success("注册用户成功", {"current_user" : get_user_from_token(token), "token" : token})
        except IntegrityError:
            raise HTTPException(status_code=500, detail="用户创建失败，请稍后重试")
        
#------------------------------
#用户登录部分,有两种登录方式，一种是手机号+密码，一种是手机号+验证码
#------------------------------

@api_user.get("/login/verification-code/send",description="发送登录验证码")
async def login_verification_code_get(phone : str):
    REDIS_USER_LOGIN_CODE = app_config.redis_config["user_login_code"]
    await get_code(phone, REDIS_USER_LOGIN_CODE)
    return ResponseModel.success("登录账号验证码发送成功")


@api_user.post("/login/verification-code-way",description="通过验证码的方式进行用户登录，此时必须输入验证码和电话，密码是null")
async def login_by_verification_code(user_login: UserLogin, response: Response):
    phone = user_login.phone
    code = user_login.code
    if code==None:
        raise HTTPException(status_code=400, detail="请输入验证码")
    REDIS_USER_LOGIN_CODE = app_config.redis_config["user_login_code"]
    await check_code(code, phone, REDIS_USER_LOGIN_CODE)

    user = await User.filter(phone = phone).first()
    if user:
        token = create_jwt(user)
        set_auth_cookie(response, token)  # 设置cookie
        return ResponseModel.success("登录成功", {"current_user" : get_user_from_token(token), "token" : token})
    else:
        raise HTTPException(status_code=404, detail="用户不存在")


@api_user.post("/login/password-way",description="通过密码的方式进行用户登录，此时必须输入密码和电话，验证码是null")
async def login_by_password(user_login: UserLogin, response: Response):
    phone = user_login.phone
    password = user_login.password
    if password==None:
        raise HTTPException(status_code=400, detail="请输入密码")
    
    user = await User.filter(phone = phone).first()
    if user:
        if user.password == md5(password):
            token = create_jwt(user)
            set_auth_cookie(response, token)  # 设置cookie
            return ResponseModel.success("登录成功", {"current_user" : get_user_from_token(token), "token" : token})
        else:
            raise HTTPException(status_code=401, detail="密码错误")
    else:
        raise HTTPException(status_code=404, detail="用户不存在")
    


@api_user.post("/logout", description="退出登录")
async def logout(request: Request, response: Response):
    token = get_token_from_request(request)
    if token:
        try:
            redis_client.set(token, 'expired', ex=60*60*24)
        except Exception as e:
            logger.warning(f"Redis操作失败，但退出登录继续: {e}")
    clear_auth_cookie(response)  # 清除cookie
    return ResponseModel.success("退出登录成功")


@api_user.post("/invalidate-cookie", description="使特定cookie失效")
async def invalidate_cookie(request: Request, response: Response, target_token: str = None):
    """
    使特定cookie失效的接口
    
    参数说明:
    - target_token: 可选，指定要失效的token。如果不提供，则使当前请求的cookie失效
    
    使用场景:
    1. 管理员强制用户下线
    2. 用户在其他设备上主动使自己的token失效
    3. 安全事件后批量使token失效
    """
    current_token = get_token_from_request(request)
    
    # 如果没有指定target_token，则使用当前请求的token
    token_to_invalidate = target_token if target_token else current_token
    
    if not token_to_invalidate:
        raise HTTPException(status_code=400, detail="没有找到要失效的token")
    
    try:
        # 验证token格式是否正确
        decode_jwt(token_to_invalidate)
        
        # 将token加入黑名单
        redis_client.set(token_to_invalidate, 'expired', ex=60*60*24*30)  # 30天过期
        
        # 如果失效的是当前请求的token，也要清除cookie
        if token_to_invalidate == current_token:
            clear_auth_cookie(response)
            
        logger.info(f"Token已失效: {token_to_invalidate[:20]}...")
        return ResponseModel.success("Cookie已成功失效")
        
    except HTTPException as e:
        # token格式无效
        if e.status_code == 401:
            raise HTTPException(status_code=400, detail="提供的token格式无效")
        raise e
    except Exception as e:
        logger.error(f"使token失效时发生错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@api_user.post("/invalidate-multiple-cookies", description="批量使多个cookie失效")
async def invalidate_multiple_cookies(request: Request, response: Response, target_tokens: list[str]):
    """
    批量使多个cookie失效的接口
    
    参数说明:
    - target_tokens: 要失效的token列表
    
    使用场景:
    1. 安全事件后批量清理
    2. 管理员批量操作
    """
    if not target_tokens:
        raise HTTPException(status_code=400, detail="请提供要失效的token列表")
    
    current_token = get_token_from_request(request)
    invalidated_count = 0
    failed_tokens = []
    current_token_invalidated = False
    
    for token in target_tokens:
        try:
            # 验证token格式是否正确
            decode_jwt(token)
            
            # 将token加入黑名单
            redis_client.set(token, 'expired', ex=60*60*24*30)  # 30天过期
            invalidated_count += 1
            
            # 检查是否包含当前请求的token
            if token == current_token:
                current_token_invalidated = True
                
        except HTTPException:
            # token格式无效，记录但继续处理其他token
            failed_tokens.append(token[:20] + "...")
        except Exception as e:
            logger.error(f"处理token时发生错误: {e}")
            failed_tokens.append(token[:20] + "...")
    
    # 如果当前token也被失效了，清除cookie
    if current_token_invalidated:
        clear_auth_cookie(response)
    
    result_message = f"成功失效 {invalidated_count} 个cookie"
    if failed_tokens:
        result_message += f"，{len(failed_tokens)} 个token处理失败"
    
    logger.info(f"批量失效操作完成: {result_message}")
    
    return ResponseModel.success(result_message, {
        "invalidated_count": invalidated_count,
        "failed_count": len(failed_tokens),
        "failed_tokens": failed_tokens,
        "current_token_invalidated": current_token_invalidated
    })


#------------------------------
#用户信息获取部分
#------------------------------

@api_user.get("/profile", description="获取当前用户个人信息（使用cookie认证）")
async def get_user_profile(request: Request):
    """
    获取当前用户的个人信息
    
    功能特点:
    - 自动从cookie或Authorization header获取认证信息
    - 返回用户基础信息
    - 支持cookie认证，无需手动传递token
    """
    try:
        # 从请求中获取当前用户信息（不检查黑名单）
        current_user = await get_user_from_request_without_blacklist(request)
        user_id = current_user.get('user_id')
        
        # 查询用户基础信息
        user = await User.get_or_none(user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 构建响应数据
        user_data = {
            "user_id": str(user.user_id),
            "account": user.account,
            "username": user.username,
            "phone": user.phone,
            "points": user.points,
            "invitation_code": user.invitation_code,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": str(user.created_at),
            "updated_at": str(user.updated_at),
            "last_login": str(user.last_login) if user.last_login else None
        }
        
        return ResponseModel.success("获取用户信息成功", user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")




