#!/usr/bin/env python3
"""
查询设备告警列表
用法: python get_alarm_list.py --sn 设备SN [--limit 数量] [--level 告警等级]

自动Token刷新：当Token失效时自动重新登录获取新Token
"""
import requests
import os
import sys
import yaml
import urllib3
import argparse
import subprocess

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "account.config")
LOGIN_SCRIPT = os.path.join(SCRIPT_DIR, "login2emu.py")
BASE_URL = "http://10.27.200.146:8090/api/ems/web"


def load_config():
    """从配置文件读取"""
    if not os.path.isfile(CONFIG_PATH):
        print("错误: 配置文件不存在，请先登录")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config


def refresh_token():
    """刷新Token"""
    config = load_config()
    user = config.get('user')
    password = config.get('password')
    
    if not user or not password:
        print("错误: 配置文件缺少用户名或密码")
        return None
    
    try:
        result = subprocess.run(
            [sys.executable, LOGIN_SCRIPT, "--user", user, "--password", password],
            capture_output=True, text=True, timeout=30, cwd=SCRIPT_DIR
        )
        if result.returncode == 0:
            new_token = result.stdout.strip()
            if new_token and new_token.startswith('eyJ'):
                print("Token已自动刷新")
                return new_token
    except Exception as e:
        print(f"Token刷新失败: {e}")
    return None


def get_alarm_list(token, page=1, limit=20, sn=None, alarm_level=None, start_time=None, end_time=None):
    """
    查询设备告警列表
    """
    url = f"{BASE_URL}/mqtt/alarm/record/getByPage"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    condition = {}
    if sn:
        condition["sn"] = sn
    if alarm_level is not None:
        condition["alarmLevel"] = alarm_level
    if start_time:
        condition["startTime"] = start_time
    if end_time:
        condition["endTime"] = end_time
    
    json_data = {"page": page, "limit": limit}
    if condition:
        json_data["condition"] = condition
    
    try:
        response = requests.post(url, json=json_data, headers=headers, verify=False, timeout=30)
        return response, response.status_code
    except Exception as e:
        print(f"请求异常: {e}")
        return None, 0


def main():
    parser = argparse.ArgumentParser(description="查询设备告警列表")
    parser.add_argument("--sn", type=str, help="设备序列号")
    parser.add_argument("--limit", type=int, default=20, help="每页数量 (默认: 20)")
    parser.add_argument("--page", type=int, default=1, help="页码 (默认: 1)")
    parser.add_argument("--level", type=int, help="告警等级 (0-严重, 1-主要, 2-次要, 3-警告)")
    parser.add_argument("--start", type=str, help="开始时间 (yyyy-MM-dd HH:mm:ss)")
    parser.add_argument("--end", type=str, help="结束时间 (yyyy-MM-dd HH:mm:ss)")
    
    args = parser.parse_args()
    
    config = load_config()
    token = config.get('token', '')
    
    if not token:
        print("错误: Token为空，请先登录")
        sys.exit(1)
    
    # 第一次请求
    response, status_code = get_alarm_list(
        token,
        page=args.page,
        limit=args.limit,
        sn=args.sn,
        alarm_level=args.level,
        start_time=args.start,
        end_time=args.end
    )
    
    # 如果Token失效，自动刷新
    if status_code in [401, 418]:
        print("Token失效，自动刷新中...")
        new_token = refresh_token()
        if new_token:
            token = new_token
            response, status_code = get_alarm_list(
                token,
                page=args.page,
                limit=args.limit,
                sn=args.sn,
                alarm_level=args.level,
                start_time=args.start,
                end_time=args.end
            )
    
    if response and status_code == 200:
        result = response.json()
        if result.get("success") == True:
            content = result.get("content", {})
            records = content.get("records", [])
            total = content.get("total", 0)
            
            print(f"共 {total} 条告警记录，显示前 {len(records)} 条：\n")
            
            level_map = {0: "严重", 1: "主要", 2: "次要", 3: "警告"}
            
            for alarm in records:
                level = level_map.get(alarm.get("alarmLevel", -1), "未知")
                print(f"设备: {alarm.get('sn', '-')}")
                print(f"告警: {alarm.get('alarmName', '-')} ({alarm.get('alarmCode', '-')})")
                print(f"等级: {level}")
                print(f"时间: {alarm.get('reportTime', '-')}")
                print("-" * 40)
        else:
            print(f"查询失败: {result.get('message', '未知错误')}")
    else:
        print(f"查询失败: HTTP {status_code}")


if __name__ == "__main__":
    main()
