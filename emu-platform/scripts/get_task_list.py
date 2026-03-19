#!/usr/bin/env python3
"""
工单任务分页查询脚本
根据条件查询EMU平台的工单任务（MqttTask主表）

用法:
    python get_task_list.py --page 1 --page-size 10
    python get_task_list.py --status 6 --page-size 20
    python get_task_list.py --name "巡检" --task-type 5
    python get_task_list.py --created-by lihairui --status 5

自动Token刷新：当Token失效时自动重新登录获取新Token
"""

import requests
import json
import os
import sys
import argparse
import urllib3
import subprocess
import yaml

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# EMU平台配置
EMU_BASE_URL = "http://10.27.200.146:8090"
API_PATH = "/api/ems/web/mqtt/workjob/task/page"

# 获取当前脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_CONFIG = os.path.join(SCRIPT_DIR, "account.config")
LOGIN_SCRIPT = os.path.join(SCRIPT_DIR, "login2emu.py")


def load_config():
    """从配置文件读取"""
    if os.path.exists(ACCOUNT_CONFIG):
        with open(ACCOUNT_CONFIG, 'r') as f:
            return yaml.safe_load(f)
    return None


def refresh_token():
    """刷新Token"""
    config = load_config()
    if not config:
        return None
    
    user = config.get('user')
    password = config.get('password')
    
    if not user or not password:
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


def load_token():
    """从配置文件加载Token"""
    config = load_config()
    if config:
        return config.get('token')
    return None


def get_task_list(token, page=1, page_size=10, **condition):
    """
    查询工单任务列表
    """
    url = f"{EMU_BASE_URL}{API_PATH}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 转换下划线为驼峰命名
    condition_camel = {}
    for key, value in condition.items():
        if value is not None:
            camel_key = ''
            next_upper = False
            for c in key:
                if c == '_':
                    next_upper = True
                else:
                    if next_upper:
                        camel_key += c.upper()
                        next_upper = False
                    else:
                        camel_key += c
            condition_camel[camel_key] = value
    
    payload = {
        "page": page,
        "pageSize": page_size,
        "condition": condition_camel
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
        return response, response.status_code
    except Exception as e:
        print(f"请求失败: {e}")
        return None, 0


def print_tasks(records):
    """格式化打印任务列表"""
    if not records:
        print("没有查询到数据")
        return
    
    print("\n" + "="*120)
    print(f"{'ID':<6} {'任务名称':<30} {'类型':<8} {'策略':<6} {'状态':<6} {'创建人':<15} {'创建时间':<20}")
    print("="*120)
    
    task_type_map = {
        0: "工作流", 1: "升级", 2: "重启", 
        3: "抓日志", 4: "shell", 5: "巡检", 
        6: "获取日志", 8: "配置项"
    }
    
    strategy_map = {1: "立即", 2: "定时", 3: "触发", 4: "周期"}
    
    status_map = {
        0: "待审批", 1: "审批中", 2: "审批不过",
        3: "未开始", 4: "进行中", 5: "成功",
        6: "失败", 7: "终止", 8: "暂停"
    }
    
    for task in records:
        task_id = task.get('id', '')
        name = task.get('name', '')[:28]
        task_type = task_type_map.get(task.get('taskType'), str(task.get('taskType')))
        strategy = strategy_map.get(task.get('scheduleStrategy'), str(task.get('scheduleStrategy')))
        status = status_map.get(task.get('status'), str(task.get('status')))
        created_by = task.get('createdBy', '')
        created_time = task.get('createdTime', '')[:19]
        
        print(f"{task_id:<6} {name:<30} {task_type:<8} {strategy:<6} {status:<6} {created_by:<15} {created_time:<20}")
    
    print("="*120)


def main():
    parser = argparse.ArgumentParser(
        description="查询EMU平台工单任务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
任务状态 (--status):
  0-待审批  1-审批中  2-审批不过  3-未开始
  4-进行中  5-成功    6-失败     7-终止    8-暂停

任务类型 (--task-type):
  0-工作流  1-升级    2-重启    3-抓日志
  4-shell   5-巡检    6-获取日志  8-配置项

示例:
  python get_task_list.py --status 5                 # 查询成功的任务
  python get_task_list.py --status 6 --page-size 20 # 查询失败的任务
  python get_task_list.py --task-type 5              # 查询巡检任务
  python get_task_list.py --created-by zhaoxinzhu     # 查询某人的任务
  python get_task_list.py --start 2026-03-18 --end 2026-03-18              # 查询今天的任务
  python get_task_list.py --start "2026-03-18 10:00:00" --end "2026-03-18 14:00:00"  # 查询指定时间范围
        """
    )
    parser.add_argument("--page", "-p", type=int, default=1, help="页码，默认1")
    parser.add_argument("--page-size", "-s", type=int, default=10, help="每页数量，默认10")
    
    # 查询条件
    parser.add_argument("--category", "-c", type=str, help="工单设备大类")
    parser.add_argument("--name", "-n", type=str, help="工单任务名称（模糊匹配）")
    parser.add_argument("--task-type", "-t", type=int, help="任务类型")
    parser.add_argument("--schedule-strategy", type=int, help="调度策略")
    parser.add_argument("--created-by", type=str, help="创建用户")
    parser.add_argument("--status", type=int, help="任务状态")
    parser.add_argument("--start", type=str, help="创建时间开始 (yyyy-MM-dd 或 yyyy-MM-dd HH:mm:ss)")
    parser.add_argument("--end", type=str, help="创建时间结束 (yyyy-MM-dd 或 yyyy-MM-dd HH:mm:ss)")
    
    args = parser.parse_args()
    
    # 加载Token
    token = load_token()
    if not token:
        print("请先运行 login2emu.py 登录获取Token")
        sys.exit(1)
    
    # 构建查询条件
    condition = {}
    if args.category:
        condition['category'] = args.category
    if args.name:
        condition['name'] = args.name
    if args.task_type is not None:
        condition['task_type'] = args.task_type
    if args.schedule_strategy is not None:
        condition['schedule_strategy'] = args.schedule_strategy
    if args.created_by:
        condition['created_by'] = args.created_by
    if args.status is not None:
        condition['status'] = args.status
    
    # 第一次请求
    response, status_code = get_task_list(token, args.page, args.page_size, **condition)
    
    # 如果Token失效，自动刷新
    if status_code in [401, 418]:
        print("Token失效，自动刷新中...")
        new_token = refresh_token()
        if new_token:
            token = new_token
            response, status_code = get_task_list(token, args.page, args.page_size, **condition)
    
    if response and status_code == 200:
        result = response.json()
        if result.get('success'):
            content = result.get('content', {})
            records = content.get('records', [])
            total = content.get('total', 0)
            pages = content.get('pages', 1)
            
            # 时间过滤（因为API对时间字段支持不完整，在客户端过滤）
            if args.start or args.end:
                filtered = []
                for r in records:
                    ct = r.get('createdTime', '')
                    # 解析创建时间
                    if not ct:
                        continue
                    # 标准化时间格式
                    if len(ct) > 19:
                        ct = ct[:19]
                    
                    # 检查是否在时间范围内
                    if args.start:
                        # 标准化开始时间
                        start = args.start.strip()
                        if len(start) == 10:  # 只有日期
                            start = start + ' 00:00:00'
                        if ct < start:
                            continue
                    if args.end:
                        # 标准化结束时间
                        end = args.end.strip()
                        if len(end) == 10:  # 只有日期
                            end = end + ' 23:59:59'
                        if ct > end:
                            continue
                    filtered.append(r)
                
                records = filtered
                total = len(records)
                pages = 1
            
            print(f"\n查询结果: 共 {total} 条记录，当前第 {args.page}/{pages} 页")
            print_tasks(records)
        else:
            print(f"查询失败: {result.get('message')}")
    else:
        print(f"查询失败: HTTP {status_code}")


if __name__ == "__main__":
    main()
