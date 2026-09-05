# 恋爱铃应用 - SQLite数据库版本

## 功能特性

- 💕 动漫风格恋爱聊天应用
- 🔐 基于SQLite的用户认证系统
- 👥 用户注册和登录
- 🎭 多角色聊天体验
- 🛡️ 安全密码哈希和IP封禁保护
- 👨‍💼 管理员后台管理

## 系统要求

- Python 3.7+
- 现代浏览器（Chrome、Firefox、Safari等）

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

#### 方法一：使用启动脚本（推荐）
```bash
python start_app.py
```

#### 方法二：分别启动前后端
```bash
# 终端1：启动后端服务器
python server.py

# 终端2：启动前端服务器
python -m http.server 8000
```

### 3. 访问应用

- 前端地址：http://localhost:8000
- 后端API：http://localhost:5000

## 默认账户

- **管理员账户**：admin / admin123
- **普通用户**：需要注册新账户

## 数据库结构

### 用户表 (users)
- `id`: 用户ID（自增）
- `username`: 用户名（唯一）
- `email`: 邮箱地址（唯一）
- `password_hash`: 密码哈希
- `salt`: 密码盐值
- `role`: 用户角色（user/admin）
- `status`: 账户状态（active/disabled）
- `created_at`: 创建时间
- `last_login`: 最后登录时间

### 登录尝试记录表 (login_attempts)
- `id`: 记录ID
- `ip_address`: IP地址
- `attempt_time`: 尝试时间
- `success`: 是否成功

### 封禁IP表 (blocked_ips)
- `id`: 记录ID
- `ip_address`: IP地址
- `blocked_at`: 封禁时间
- `unblock_at`: 解封时间
- `reason`: 封禁原因

## API接口

### 用户注册
```
POST /api/register
Content-Type: application/json

{
    "username": "用户名",
    "email": "邮箱",
    "password": "密码"
}
```

### 用户登录
```
POST /api/login
Content-Type: application/json

{
    "username": "用户名",
    "password": "密码",
    "remember_me": false
}
```

### 获取用户列表（管理员）
```
GET /api/users
```

### 更新用户信息（管理员）
```
PUT /api/user/{user_id}
Content-Type: application/json

{
    "email": "新邮箱",
    "role": "admin",
    "status": "active",
    "password": "新密码"
}
```

### 获取封禁IP列表（管理员）
```
GET /api/blocked-ips
```

### 清除封禁IP（管理员）
```
DELETE /api/blocked-ips
```

### 获取系统统计（管理员）
```
GET /api/stats
```

## 安全特性

- 🔐 密码使用SHA256哈希 + 随机盐值
- 🛡️ IP封禁保护（防止暴力破解）
- 📊 登录尝试记录和统计
- 👨‍💼 管理员权限控制
- 🔒 账户状态管理

## 故障排除

### 1. 端口被占用
如果5000或8000端口被占用，可以修改端口：
- 后端：修改 `server.py` 中的 `app.run(port=5000)`
- 前端：修改启动命令中的端口号

### 2. 数据库文件权限
确保应用有权限创建和写入 `users.db` 文件

### 3. 跨域问题
如果遇到跨域问题，检查CORS配置是否正确

### 4. 依赖问题
如果遇到模块导入错误，请确保已安装所有依赖：
```bash
pip install Flask Flask-CORS
```

## 开发说明

### 数据库文件
- 数据库文件：`users.db`
- 首次运行时会自动创建数据库和表结构
- 会自动创建默认管理员账户

### 日志查看
- 后端日志会显示在控制台
- 前端日志可以在浏览器开发者工具中查看

### 数据备份
建议定期备份 `users.db` 文件以保护用户数据

## 许可证

本项目仅供学习和演示使用。 