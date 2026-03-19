import requests
import hashlib
import os
import datetime
import yaml
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 获取当前脚本的绝对路径
current_path = os.path.dirname(os.path.abspath(__file__))

def login(url, username, password, verificationCode="starnet"):
    """
    登录成功返回token，失败返回False
    """
    password_md5 = hashlib.md5(
        (hashlib.md5(password.encode('utf-8')).hexdigest() + "starnet").encode("utf-8")
    ).hexdigest()
    
    json_data = {
        "username": username,
        "password": password_md5,
        "verificationCode": verificationCode
    }
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    headers = {"User-Agent": user_agent}
    
    try:
        response = requests.post(url, json=json_data, verify=False, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") == True:
                token = result["content"]["accessToken"]
                account_path = os.path.join(current_path, "account.config")
                
                # 读取或初始化配置
                if os.path.isfile(account_path):
                    with open(account_path, 'r') as f:
                        config = yaml.safe_load(f) or {}
                else:
                    config = {}
                
                # 更新token和过期时间
                config["user"] = username
                config["password"] = password
                config["token"] = token
                config["token_time"] = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                
                with open(account_path, 'w') as f:
                    yaml.dump(config, f)
                
                return token
    except Exception as e:
        print(f"登录请求失败: {e}")
    
    return False


def verify(url, username, password):
    """验证登录结果"""
    return login(url, username, password)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="登录EMU平台")
    parser.add_argument("--user", type=str, required=True, help="用户名")
    parser.add_argument("--password", type=str, required=True, help="密码")
    args = parser.parse_args()
    
    # 8090端口直连后台，HTTP协议
    url = "http://10.27.200.146:8090/api/ems/web/login"
    
    res = login(url, args.user, args.password)
    print(res)
