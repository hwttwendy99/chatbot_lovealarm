#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证服务器
使用SQLite数据库存储用户信息
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import os
import secrets
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据库配置
DATABASE = 'users.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 创建登录尝试记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # 创建被封禁的IP表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE NOT NULL,
            blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            unblock_at TIMESTAMP,
            reason TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def hash_password(password, salt):
    """哈希密码"""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_salt():
    """生成随机盐值"""
    return secrets.token_hex(16)

def get_client_ip():
    """获取客户端IP"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def is_ip_blocked(ip):
    """检查IP是否被封禁"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT unblock_at FROM blocked_ips 
        WHERE ip_address = ? AND unblock_at > CURRENT_TIMESTAMP
    ''', (ip,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

def record_login_attempt(ip, success):
    """记录登录尝试"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO login_attempts (ip_address, success)
        VALUES (?, ?)
    ''', (ip, success))
    
    conn.commit()
    conn.close()

def check_failed_attempts(ip, max_attempts=5, window_minutes=30):
    """检查失败登录次数"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM login_attempts 
        WHERE ip_address = ? 
        AND success = FALSE 
        AND attempt_time > datetime('now', '-{} minutes')
    '''.format(window_minutes), (ip,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count >= max_attempts

def block_ip(ip, duration_hours=24):
    """封禁IP"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    unblock_time = datetime.now().replace(microsecond=0)
    unblock_time = unblock_time.replace(hour=unblock_time.hour + duration_hours)
    
    cursor.execute('''
        INSERT OR REPLACE INTO blocked_ips (ip_address, unblock_at, reason)
        VALUES (?, ?, ?)
    ''', (ip, unblock_time.isoformat(), 'Too many failed login attempts'))
    
    conn.commit()
    conn.close()

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # 验证输入
        if not username or not email or not password:
            return jsonify({'error': '请填写所有必填字段'}), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须为3-20个字符'}), 400
        
        if len(password) < 6:
            return jsonify({'error': '密码长度至少为6位'}), 400
        
        # 检查用户名和邮箱是否已存在
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': '用户名已存在'}), 400
        
        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建用户
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, salt, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, salt, 'user', 'active'))
        
        user_id = cursor.lastrowid
        
        # 获取用户信息
        cursor.execute('''
            SELECT id, username, email, role, status, created_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        conn.commit()
        conn.close()
        
        user = {
            'id': user_data[0],
            'username': user_data[1],
            'email': user_data[2],
            'role': user_data[3],
            'status': user_data[4],
            'created_at': user_data[5]
        }
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': user
        })
        
    except Exception as e:
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        ip = get_client_ip()
        
        # 检查IP是否被封禁
        if is_ip_blocked(ip):
            return jsonify({'error': '您的IP已被封禁，请稍后再试'}), 403
        
        # 检查失败登录次数
        if check_failed_attempts(ip):
            block_ip(ip)
            return jsonify({'error': '登录失败次数过多，IP已被封禁'}), 403
        
        # 验证输入
        if not username or not password:
            record_login_attempt(ip, False)
            return jsonify({'error': '请输入用户名和密码'}), 400
        
        # 查找用户
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, password_hash, salt, role, status
            FROM users WHERE username = ?
        ''', (username,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            record_login_attempt(ip, False)
            conn.close()
            return jsonify({'error': '用户名或密码错误'}), 401
        
        user_id, db_username, email, password_hash, salt, role, status = user_data
        
        # 检查账户状态
        if status != 'active':
            conn.close()
            return jsonify({'error': '账户已被禁用'}), 403
        
        # 验证密码
        if hash_password(password, salt) != password_hash:
            record_login_attempt(ip, False)
            conn.close()
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 登录成功
        record_login_attempt(ip, True)
        
        # 更新最后登录时间
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        user = {
            'id': user_id,
            'username': db_username,
            'email': email,
            'role': role,
            'status': status
        }
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': user
        })
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取所有用户（管理员功能）"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role, status, created_at, last_login
            FROM users ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'status': row[4],
                'created_at': row[5],
                'last_login': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'users': users
        })
        
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500

@app.route('/api/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息（管理员功能）"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': '用户不存在'}), 404
        
        # 更新用户信息
        updates = []
        params = []
        
        if 'email' in data:
            updates.append('email = ?')
            params.append(data['email'])
        
        if 'role' in data:
            updates.append('role = ?')
            params.append(data['role'])
        
        if 'status' in data:
            updates.append('status = ?')
            params.append(data['status'])
        
        if 'password' in data and data['password']:
            salt = generate_salt()
            password_hash = hash_password(data['password'], salt)
            updates.append('password_hash = ?')
            updates.append('salt = ?')
            params.extend([password_hash, salt])
        
        if updates:
            params.append(user_id)
            query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '用户信息更新成功'
        })
        
    except Exception as e:
        return jsonify({'error': f'更新用户信息失败: {str(e)}'}), 500

@app.route('/api/blocked-ips', methods=['GET'])
def get_blocked_ips():
    """获取被封禁的IP列表（管理员功能）"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ip_address, blocked_at, unblock_at, reason
            FROM blocked_ips 
            WHERE unblock_at > CURRENT_TIMESTAMP
            ORDER BY blocked_at DESC
        ''')
        
        blocked_ips = []
        for row in cursor.fetchall():
            blocked_ips.append({
                'ip_address': row[0],
                'blocked_at': row[1],
                'unblock_at': row[2],
                'reason': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'blocked_ips': blocked_ips
        })
        
    except Exception as e:
        return jsonify({'error': f'获取封禁IP列表失败: {str(e)}'}), 500

@app.route('/api/blocked-ips', methods=['DELETE'])
def clear_blocked_ips():
    """清除所有封禁的IP（管理员功能）"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM blocked_ips')
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '所有封禁IP已清除'
        })
        
    except Exception as e:
        return jsonify({'error': f'清除封禁IP失败: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取系统统计信息（管理员功能）"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 用户统计
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        admin_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE status = "active"')
        active_users = cursor.fetchone()[0]
        
        # 登录尝试统计
        cursor.execute('SELECT COUNT(*) FROM login_attempts WHERE success = TRUE')
        successful_logins = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM login_attempts WHERE success = FALSE')
        failed_logins = cursor.fetchone()[0]
        
        # 封禁IP统计
        cursor.execute('SELECT COUNT(*) FROM blocked_ips WHERE unblock_at > CURRENT_TIMESTAMP')
        blocked_ips_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'admin_users': admin_users,
                'active_users': active_users,
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'blocked_ips': blocked_ips_count
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 创建默认管理员账户
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT username FROM users WHERE username = "admin"')
    if not cursor.fetchone():
        salt = generate_salt()
        password_hash = hash_password('admin123', salt)
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, salt, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@chatbot.com', password_hash, salt, 'admin', 'active'))
        
        print("默认管理员账户已创建: admin / admin123")
    
    conn.commit()
    conn.close()
    
    print("服务器启动中...")
    app.run(debug=True, host='0.0.0.0', port=5001) 