#!/usr/bin/env python3
"""
设备完整信息查询
支持模板自定义输出格式
"""
import requests
import yaml
import urllib3
import subprocess
import sys
import os
import argparse
import re
urllib3.disable_warnings()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "account.config")
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "..", "templates")

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def refresh_token():
    config = load_config()
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "login2emu.py"), 
             "--user", config.get('user', ''), "--password", config.get('password', '')],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def get_device_all(token, sn):
    """获取设备完整信息"""
    base_url = "http://10.27.200.146:8090/api/ems/web"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    result = {'sn': sn, 'online': False}
    
    # 基本信息
    url = f"{base_url}/mqtt/gw/{sn}/GET_DETAIL_INFO/cmd"
    try:
        resp = requests.post(url, json={}, headers=headers, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                c = data.get('content', {})
                result.update({
                    'online': c.get('status') == '0',
                    'model': c.get('model', '-'),
                    'vendor': c.get('vendor', '-'),
                    'mac': c.get('mac', '-'),
                    'ip': c.get('ipv4', '-'),
                    'cpu': c.get('cpuPercent', '-'),
                    'memory': c.get('memoryPercent', '-'),
                    'temp': c.get('cpuTemperature', '-'),
                    'uptime': c.get('runTime', '0'),
                    'first_online': c.get('firstConnectTime', '-'),
                })
    except:
        pass
    
    # WiFi
    url = f"{base_url}/mqtt/gw/{sn}/GET_WIFI_INFO/cmd"
    try:
        resp = requests.post(url, json={}, headers=headers, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                result['wifi'] = data.get('content', {}).get('list', [])
    except:
        pass
    
    # LAN
    url = f"{base_url}/mqtt/gw/{sn}/GET_LAN_PORT_LIST_INFO/cmd"
    try:
        resp = requests.post(url, json={}, headers=headers, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                result['lan'] = data.get('content', {}).get('list', [])
    except:
        pass
    
    # PON
    url = f"{base_url}/mqtt/gw/{sn}/GET_UP_AND_DOWN_PON_INFO/cmd"
    try:
        resp = requests.post(url, json={}, headers=headers, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                result['pon'] = data.get('content', {})
    except:
        pass
    
    return result

def format_uptime(seconds):
    """格式化运行时间"""
    try:
        s = int(seconds)
        d = s // 86400
        h = (s % 86400) // 3600
        m = (s % 3600) // 60
        if d > 0:
            return f"{d}天{h}时{m}分"
        return f"{h}时{m}分"
    except:
        return "-"

def load_template(name):
    """加载模板文件"""
    template_path = os.path.join(TEMPLATE_DIR, name)
    if os.path.isfile(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def render_template(template, data):
    """渲染模板"""
    if not template:
        return None
    
    # 基础字段
    replacements = {
        '{sn}': data.get('sn', '-'),
        '{status}': '在线' if data.get('online') else '离线',
        '{status_icon}': '✅' if data.get('online') else '❌',
        '{model}': data.get('model', '-'),
        '{vendor}': data.get('vendor', '-'),
        '{mac}': data.get('mac', '-'),
        '{ip}': data.get('ip', '-'),
        '{cpu}': data.get('cpu', '-'),
        '{memory}': data.get('memory', '-'),
        '{temp}': data.get('temp', '-'),
        '{uptime}': format_uptime(data.get('uptime', '0')),
        '{first_online}': data.get('first_online', '-')[:19] if data.get('first_online') else '-',
        '{newline}': '\n',
    }
    
    # 温度警告
    try:
        temp_warn = '⚠️' if int(data.get('temp', 0)) > 70 else ''
    except:
        temp_warn = ''
    replacements['{temp_warn}'] = temp_warn
    
    # WiFi列表 - 表格行格式
    wifi_list = []
    for w in data.get('wifi', []):
        if w.get('enable') == '1':
            encrypt_map = {'4': 'WPA3', '5': 'WPA2', '1': 'WPA', '0': '开放'}
            encrypt = encrypt_map.get(w.get('encrypt', ''), w.get('encrypt', '-'))
            wifi_list.append(f"| {w.get('name')} | {w.get('radioType')} | {encrypt} |")
    replacements['{wifi_list}'] = '\n'.join(wifi_list) if wifi_list else ''
    data['wifi_list'] = wifi_list  # 用于条件判断
    
    # LAN已连接
    lan_conn = []
    for l in data.get('lan', []):
        if l.get('connect'):
            lan_conn.append(l.get('name', '-'))
    lan_str = ', '.join(lan_conn) if lan_conn else ''
    replacements['{lan_conn}'] = lan_str
    data['lan_conn'] = lan_conn  # 用于条件判断
    
    # 光功率
    pon = data.get('pon', {})
    up_power = pon.get('upInputPower', '')
    down_power = pon.get('downTxPower', '')
    replacements['{up_power}'] = up_power if up_power else '-'
    replacements['{down_power}'] = down_power if down_power else '-'
    data['up_power'] = up_power  # 用于条件判断
    
    # 处理条件块 {if xxx}...{endif}
    def process_condition(match):
        key = match.group(1)
        content = match.group(2)
        value = data.get(key)
        # 非空才显示
        if not value:
            return ''
        if isinstance(value, list) and len(value) == 0:
            return ''
        # 替换条件块内的变量
        for k, v in replacements.items():
            content = content.replace(k, str(v))
        return content
    
    result = template
    for key, value in replacements.items():
        result = result.replace(key, str(value))
    
    result = re.sub(r'\{if\s+(\w+)\}(.*?)\{endif\}', process_condition, result, flags=re.DOTALL)
    
    return result

def print_with_template(data, template):
    """使用模板输出"""
    rendered = render_template(template, data)
    if rendered:
        print(rendered)
    else:
        # 回退到默认格式
        print_device_default(data)

def render_batch_template(template, devices):
    """渲染批量对比模板"""
    if not template or len(devices) < 1:
        return None
    
    # 构建替换字典
    replacements = {}
    for i, dev in enumerate(devices, 1):
        status_icon = "✅" if dev.get('online') else "❌"
        status_text = "在线" if dev.get('online') else "离线"
        try:
            temp_warn = " ⚠️" if int(dev.get('temp', 0)) > 70 else ""
        except:
            temp_warn = ""
        
        # 格式化WiFi列表
        wifi_list = []
        for w in dev.get('wifi', []):
            if w.get('enable') == '1':
                wifi_list.append(w.get('name', '-'))
        
        # LAN已连接
        lan_conn = []
        for l in dev.get('lan', []):
            if l.get('connect'):
                lan_conn.append(l.get('name', '-'))
        
        # 光功率
        pon = dev.get('pon', {})
        
        replacements[f'sn{i}'] = dev.get('sn', '-')
        replacements[f'status{i}'] = status_icon
        replacements[f'model{i}'] = dev.get('model', '-')
        replacements[f'vendor{i}'] = dev.get('vendor', '-')
        replacements[f'mac{i}'] = dev.get('mac', '-')
        replacements[f'ip{i}'] = dev.get('ip', '-')
        replacements[f'cpu{i}'] = dev.get('cpu', '-')
        replacements[f'memory{i}'] = dev.get('memory', '-')
        replacements[f'temp{i}'] = dev.get('temp', '-')
        replacements[f'temp_warn{i}'] = temp_warn
        replacements[f'uptime{i}'] = format_uptime(dev.get('uptime', '0'))
        replacements[f'first_online{i}'] = dev.get('first_online', '-')[:10] if dev.get('first_online') else '-'
        replacements[f'lan{i}'] = ', '.join(lan_conn) if lan_conn else '-'
        replacements[f'up_power{i}'] = pon.get('upInputPower', '-')
        replacements[f'down_power{i}'] = pon.get('downTxPower', '-')
        replacements[f'wifi{i}'] = ', '.join(wifi_list[:3]) if wifi_list else '-'
    
    # 填充剩余设备列
    for i in range(len(devices) + 1, 10):
        for key in ['sn', 'status', 'model', 'ip', 'cpu', 'memory', 'temp', 'uptime', 'first_online', 'lan', 'up_power', 'down_power', 'wifi', 'temp_warn']:
            replacements[f'{key}{i}'] = '-'
    
    # 替换
    result = template
    for key, value in replacements.items():
        result = result.replace(f'{{{key}}}', str(value))
    
    return result

def print_batch_template(devices, template):
    """使用批量对比模板输出"""
    rendered = render_batch_template(template, devices)
    if rendered:
        print(rendered)
    else:
        # 回退到单设备输出
        for dev in devices:
            print_device_default(dev)
            print()

def print_device_default(dev):
    """默认输出格式"""
    status_icon = "✅" if dev['online'] else "❌"
    status_text = "在线" if dev['online'] else "离线"
    temp_warn = ""
    try:
        if int(dev.get('temp', 0)) > 70:
            temp_warn = " ⚠️"
    except:
        pass
    
    print(f"{'─'*50}")
    print(f"{status_icon} {dev['sn']} [{status_text}]")
    print(f"{'─'*50}")
    
    if not dev['online']:
        print("  设备离线，无法获取更多信息")
        return
    
    print(f"  型号: {dev['model']} ({dev['vendor']})")
    print(f"  MAC: {dev['mac']}")
    print(f"  IP: {dev['ip']}")
    print(f"  CPU: {dev['cpu']}%  内存: {dev['memory']}%  温度: {dev['temp']}°C{temp_warn}")
    print(f"  运行: {format_uptime(dev['uptime'])}  入网: {dev['first_online'][:10] if dev['first_online'] else '-'}")
    
    if dev.get('wifi'):
        wifi = [w for w in dev['wifi'] if w.get('enable') == '1']
        if wifi:
            print(f"\n  📶 WiFi:")
            for w in wifi:
                print(f"    • {w.get('name')} ({w.get('radioType')})")
    
    if dev.get('lan'):
        connected = [l for l in dev['lan'] if l.get('connect')]
        if connected:
            print(f"\n  🔌 LAN已连接: {len(connected)}个")
            for l in connected:
                print(f"    • {l.get('name')}")
    
    if dev.get('pon'):
        pon = dev['pon']
        print(f"\n  📡 光功率: 上行{pon.get('upInputPower')} / 下行{pon.get('downTxPower')}")

def main():
    parser = argparse.ArgumentParser(description="查询设备完整信息")
    parser.add_argument("--sn", help="单个设备SN")
    parser.add_argument("--sn-list", help="设备SN列表（逗号分隔）")
    parser.add_argument("--file", help="从文件读取设备列表")
    parser.add_argument("--template", "-t", help="模板文件名（如 device_single.txt）")
    parser.add_argument("--simple", action="store_true", help="简洁模式（无WiFi/LAN详情）")
    
    args = parser.parse_args()
    
    # 收集SN
    sn_list = []
    if args.sn:
        sn_list.append(args.sn)
    if args.sn_list:
        sn_list.extend([s.strip() for s in args.sn_list.split(',') if s.strip()])
    if args.file and os.path.isfile(args.file):
        with open(args.file) as f:
            sn_list.extend([l.strip() for l in f if l.strip()])
    
    if not sn_list:
        parser.print_help()
        return
    
    sn_list = list(set(sn_list))
    
    # 加载模板
    template = None
    batch_template = None
    if args.template:
        template = load_template(args.template)
        # 尝试加载批量对比模板
        batch_tpl_name = args.template.replace('_single', '_batch')
        batch_template = load_template(batch_tpl_name)
    
    # 获取token
    config = load_config()
    token = config.get('token', '')
    if not token:
        print("错误: Token为空")
        return
    
    # 批量查询所有设备
    all_devices = []
    for sn in sn_list:
        dev = get_device_all(token, sn)
        all_devices.append(dev)
    
    # 判断使用哪种模板
    if len(sn_list) > 1 and batch_template:
        print(f"\n{'='*60}")
        print(f"📊 设备对比查询 ({len(sn_list)}台)")
        print(f"{'='*60}\n")
        print_batch_template(all_devices, batch_template)
    else:
        print(f"\n{'='*50}")
        print(f"📊 设备完整信息查询 ({len(sn_list)}台)")
        print(f"{'='*50}\n")
        for i, dev in enumerate(all_devices, 1):
            print(f"[{i}/{len(sn_list)}] {dev['sn']}")
            print_with_template(dev, template)
            print()

if __name__ == "__main__":
    main()
