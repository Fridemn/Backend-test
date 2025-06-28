# 通用设计

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
```bash
# 初始化配置文件
python -m app.config.config_manager init

# 编辑 .env 文件，填入正确的PostgreSQL数据库和其他服务配置
# 编辑 data/config.json 文件，调整应用配置
```

### 3. 配置PostgreSQL数据库
确保PostgreSQL服务正在运行，并在 `.env` 文件中配置正确的连接信息：
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=your_database
```

### 4. 初始化数据库
```bash
# 初始化数据库结构
python migration.py init

# 检查数据库连接
python migration.py check

# 创建示例数据（可选）
python migration.py sample
```

### 5. 验证配置
```bash
# 检查配置文件状态
python -m app.config.config_manager check

# 验证配置文件
python -m app.config.config_manager validate
```

### 6. 运行应用
```bash
python main.py
```

## 数据库架构

项目使用PostgreSQL作为主数据库，通过Tortoise ORM进行数据访问：

### 数据表结构
- **users**: 用户基础信息表
- **user_profiles**: 用户详细信息表  
- **user_vip**: 用户会员信息表
- **user_identities**: 用户身份信息表

### 数据库特性
- 使用UUID作为主键
- 支持JSON字段存储复杂数据
- 完善的索引设计
- 事务支持
- 外键约束

## 配置文件说明

项目使用分离的配置管理架构：

### 环境变量文件 (.env)
存储敏感信息，不会被提交到版本控制：
- PostgreSQL数据库连接信息
- Redis 配置
- JWT 密钥
- 第三方服务 API 密钥

### 基础配置文件 (data/config.json)
存储非敏感的应用配置：
- 用户积分配置
- 应用设置
- 缓存配置
- 日志配置

### 模板文件
- `.env.example`: 环境变量模板
- `config.json.example`: 配置文件模板

## 数据库迁移

### 从MySQL迁移到PostgreSQL
```bash
# 1. 备份MySQL数据（手动导出为JSON）
# 2. 初始化PostgreSQL数据库
python migration.py init

# 3. 从备份文件迁移数据
python migration.py migrate backup.json

# 4. 查看迁移结果
python migration.py stats
```

### 数据库维护命令
```bash
# 检查数据库连接
python migration.py check

# 创建示例数据
python migration.py sample

# 查看数据库统计
python migration.py stats
```

## 项目结构

分离用户
基础信息
    user_id，phone, account,username, password
详细信息
    gender, age, birthday, address, avatar, nickname, signature,email
会员信息
    vip_level, vip_start_time, vip_end_time, vip_type
身份信息
    identity_type



还需要做的，统一终端日志输出，日志文件输出等等
函数类型声明

能否检查非空参数