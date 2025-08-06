#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 同时运行前端和后端服务器
"""

import subprocess
import sys
import time
import os
import signal
import threading

def run_server(port, description):
    """运行服务器"""
    try:
        if port == 5000:
            # 后端服务器
            subprocess.run([sys.executable, 'server.py'], check=True)
        else:
            # 前端服务器
            subprocess.run([sys.executable, '-m', 'http.server', str(port)], check=True)
    except KeyboardInterrupt:
        print(f"\n{description} 已停止")
    except Exception as e:
        print(f"{description} 启动失败: {e}")

def main():
    print("🚀 启动恋爱铃应用...")
    print("=" * 50)
    
    # 检查依赖
    try:
        import flask
        import flask_cors
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 启动后端服务器
    print("🔧 启动后端服务器 (端口 5000)...")
    backend_thread = threading.Thread(
        target=run_server, 
        args=(5000, "后端服务器"),
        daemon=True
    )
    backend_thread.start()
    
    # 等待后端服务器启动
    time.sleep(2)
    
    # 启动前端服务器
    print("🌐 启动前端服务器 (端口 8000)...")
    frontend_thread = threading.Thread(
        target=run_server, 
        args=(8000, "前端服务器"),
        daemon=True
    )
    frontend_thread.start()
    
    print("=" * 50)
    print("🎉 应用启动完成!")
    print("📱 前端地址: http://localhost:8000")
    print("🔧 后端API: http://localhost:5000")
    print("=" * 50)
    print("按 Ctrl+C 停止所有服务器")
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务器...")
        sys.exit(0)

if __name__ == '__main__':
    main() 