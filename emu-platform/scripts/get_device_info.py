#!/usr/bin/env python3
"""
查询设备基础信息
用法: python get_device_info.py --sn 设备SN

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

# 获取脚本所在目录
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


def get_device_info(token, device_sn, cmd_type="GET_DETAIL_INFO"):
    """
    查询设备信息
    """
    url = f"{BASE_URL}/mqtt/gw/{device_sn}/{cmd_type}/cmd"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json={}, headers=headers, verify=False, timeout=30)
        return response, response.status_code
    except Exception as e:
        print(f"请求异常: {e}")
        return None, 0


def main():
    parser = argparse.ArgumentParser(
        description="查询设备基础信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 查询单个设备
  python get_device_info.py --sn STAR17604308
  
  # 批量查询多个设备（逗号分隔）
  python get_device_info.py --sn-list STAR17604308,STAR17604298,STAR1769A618
  
  # 从文件读取设备列表
  python get_device_info.py --file device_list.txt
  
  # 指定命令类型
  python get_device_info.py --sn STAR17604308 --cmd GET_WIFI_INFO
        """
    )
    parser.add_argument("--sn", type=str, help="设备序列号（单个）")
    parser.add_argument("--sn-list", type=str, help="设备序列号列表（逗号分隔，如: SN1,SN2,SN3）")
    parser.add_argument("--file", type=str, help="从文件读取设备SN列表（每行一个）")
    parser.add_argument("--cmd", type=str, default="GET_DETAIL_INFO", 
                        help="命令类型 (默认: GET_DETAIL_INFO)")
    parser.add_argument("--quiet", action="store_true", help="静默模式，减少输出")
    parser.add_argument("--detail", action="store_true", help="详细模式，显示完整信息")
    
    args = parser.parse_args()
    
    config = load_config()
    token = config.get('token', '')
    
    if not token:
        print("错误: Token为空，请先登录")
        sys.exit(1)
    
    # 收集设备SN列表
    sn_list = []
    
    if args.sn:
        sn_list.append(args.sn)
    
    if args.sn_list:
        sn_list.extend([s.strip() for s in args.sn_list.split(',') if s.strip()])
    
    if args.file:
        if os.path.isfile(args.file):
            with open(args.file, 'r') as f:
                sn_list.extend([line.strip() for line in f if line.strip()])
        else:
            print(f"错误: 文件不存在 {args.file}")
            sys.exit(1)
    
    # 如果没有指定设备，报错
    if not sn_list:
        parser.print_help()
        sys.exit(1)
    
    # 去重
    sn_list = list(set(sn_list))
    
    if not args.quiet:
        print(f"将查询 {len(sn_list)} 个设备...")
        print("=" * 60)
    
    # 批量查询
    success_count = 0
    fail_count = 0
    
    for i, sn in enumerate(sn_list, 1):
        if not args.quiet:
            print(f"\n[{i}/{len(sn_list)}] 查询设备: {sn}")
        
        response, status_code = get_device_info(token, sn, args.cmd)
        
        # Token失效处理
        if status_code in [401, 418]:
            if not args.quiet:
                print("  Token失效，刷新中...")
            new_token = refresh_token()
            if new_token:
                token = new_token
                response, status_code = get_device_info(token, sn, args.cmd)
        
        if response and status_code == 200:
            result = response.json()
            if result.get('success'):
                success_count += 1
                if not args.quiet:
                    content = result.get('content', {})
                    
                    # 判断是简洁模式还是详细模式
                    if args.detail:
                        # 详细模式
                        print(f"\n{'='*60}")
                        print(f"设备: {sn}")
                        print(f"{'='*60}")
                        
                        status_map = {'0': '在线', '1': '离线'}
                        status = status_map.get(content.get('status', ''), content.get('status', '未知'))
                        
                        print(f"状态:        {status}")
                        print(f"型号:        {content.get('model', '未知')}")
                        print(f"厂商:        {content.get('vendor', '未知')}")
                        print(f"MAC:         {content.get('mac', '未知')}")
                        print(f"固件版本:    {content.get('firmwareVer', '未知')}")
                        print(f"硬件版本:    {content.get('hardwareVer', '未知')}")
                        print(f"IP地址:      {content.get('ipv4', '未知')}")
                        print(f"注册IP:      {content.get('netIp', '未知')}")
                        print(f"PPPoE账号:   {content.get('pppoeAcc', '未知')}")
                        print(f"上线速率:    {content.get('upRate', '?')} Mbps")
                        print(f"下行速率:    {content.get('downRate', '?')} Mbps")
                        print(f"CPU使用率:   {content.get('cpuPercent', '?')}%")
                        print(f"CPU温度:     {content.get('cpuTemperature', '?')}°C")
                        print(f"内存使用率:  {content.get('memoryPercent', '?')}%")
                        print(f"运行时间:    {content.get('runTime', '?')}秒")
                        print(f"首次入网:    {content.get('firstConnectTime', '未知')}")
                    else:
                        # 简洁模式
                        status = content.get('status', '?')
                        model = content.get('model', '未知')
                        vendor = content.get('vendor', '未知')
                        cpu = content.get('cpuPercent', '?')
                        memory = content.get('memoryPercent', '?')
                        print(f"  ✅ {model} ({vendor}) - CPU:{cpu}% 内存:{memory}%")
            else:
                fail_count += 1
                if not args.quiet:
                    print(f"  ❌ 查询失败: {result.get('message', '未知错误')}")
        else:
            fail_count += 1
            if not args.quiet:
                print(f"  ❌ HTTP错误: {status_code}")
    
    # 输出统计
    if not args.quiet:
        print("\n" + "=" * 60)
        print(f"查询完成: 成功 {success_count}, 失败 {fail_count}")
    else:
        # 静默模式只输出结果
        print(f"成功:{success_count} 失败:{fail_count} 总计:{len(sn_list)}")


if __name__ == "__main__":
    main()
