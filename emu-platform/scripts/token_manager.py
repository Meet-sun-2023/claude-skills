#!/usr/bin/env python3
"""
Token管理器 - 自动刷新失效的Token

提供get_valid_token()函数，自动检测Token是否失效，
如果失效则自动重新登录获取新Token。
"""

import os
import sys
import subprocess
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 脚本目录和配置文件
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "account.config")
LOGIN_SCRIPT = os.path.join(SCRIPT_DIR, "login2emu.py")


def load_config():
    """加载配置文件"""
    import yaml
    if not os.path.isfile(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_valid_token():
    """
    获取有效的Token
    
    自动检测Token是否失效：
    - 如果失效（返回401/418），自动调用login2emu.py重新登录
    - 返回最新的有效Token
    
    Returns:
        str: 有效的Token
        None: 如果无法获取Token
    """
    config = load_config()
    
    if not config:
        print("错误: 配置文件不存在，请先登录")
        return None
    
    user = config.get('user')
    password = config.get('password')
    current_token = config.get('token')
    
    if not user or not password:
        print("错误: 配置文件缺少用户名或密码，请先配置")
        return None
    
    return current_token


def refresh_token():
    """
    强制刷新Token
    
    重新调用登录脚本获取新Token
    
    Returns:
        str: 新的Token
        None: 如果刷新失败
    """
    config = load_config()
    
    if not config:
        print("错误: 配置文件不存在")
        return None
    
    user = config.get('user')
    password = config.get('password')
    
    if not user or not password:
        print("错误: 配置文件缺少用户名或密码")
        return None
    
    try:
        # 调用登录脚本
        result = subprocess.run(
            [sys.executable, LOGIN_SCRIPT, "--user", user, "--password", password],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=SCRIPT_DIR
        )
        
        if result.returncode == 0:
            new_token = result.stdout.strip()
            if new_token and new_token.startswith('eyJ'):
                print(f"Token刷新成功")
                return new_token
            else:
                print(f"Token刷新失败: {new_token}")
                return None
        else:
            print(f"Token刷新失败: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Token刷新超时")
        return None
    except Exception as e:
        print(f"Token刷新异常: {e}")
        return None


def request_with_auto_retry(request_func, *args, **kwargs):
    """
    带自动重试的请求包装器
    
    如果请求返回401/418，自动刷新Token并重试
    
    Args:
        request_func: 请求函数，第一个参数必须是token
        *args, **kwargs: 传递给request_func的其他参数
        
    Returns:
        请求结果
        
    Usage:
        result = request_with_auto_retry(
            get_device_info, 
            "STAR123456",
            cmd_type="GET_DETAIL_INFO"
        )
    """
    config = load_config()
    if not config:
        return None
    
    user = config.get('user')
    password = config.get('password')
    
    # 首次尝试
    current_token = get_valid_token()
    if not current_token:
        return None
    
    # 第一次请求
    result = request_func(current_token, *args, **kwargs)
    
    # 检查是否需要刷新Token
    if result is not None and isinstance(result, dict):
        # 检查返回状态
        status = result.get('status_code') or (200 if result.get('success') is not False else 401)
        
        if status in [401, 418]:
            print("Token失效，尝试刷新...")
            new_token = refresh_token()
            if new_token:
                # 用新Token重试
                result = request_func(new_token, *args, **kwargs)
    
    return result


if __name__ == "__main__":
    # 测试
    print("测试获取Token...")
    token = get_valid_token()
    if token:
        print(f"当前Token: {token[:50]}...")
    else:
        print("获取Token失败")
