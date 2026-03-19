---
name: emu-platform
description: EMU平台集成 - 在EMU平台上查询设备信息(可以指定设备sn)、任务状态、告警事件诊断
---

# emu-platform

EMU平台集成，实现设备查询、任务管理、告警诊断等功能。

## 触发条件

- 用户要求查询EMU平台上的设备信息
- 用户要求查询任务状态
- 用户要求进行告警事件诊断
- 用户要求查看设备告警历史

## 配置文件

在执行任何操作前，需要确保配置文件存在：

- **配置文件路径**：`~/.openclaw/skills/emu-platform/scripts/account.config`
- **登录脚本路径**：`~/.openclaw/skills/emu-platform/scripts/login2emu.py`

### 配置字段

EMU平台基础地址已内置为：`http://10.27.200.146:8090`

## 认证流程

### 首次使用：账号配置

**配置文件**：`~/.openclaw/skills/emu-platform/scripts/account.config`

配置文件包含以下字段：
- `user`: 用户名
- `password`: 密码
- `token`: 登录Token
- `token_time`: Token过期时间

**自动检测逻辑**：
1. 读取 `account.config` 文件
2. 检查 `user` 和 `password` 字段是否存在
3. 如果不存在或为空，**提示用户输入账号密码**

### Token管理（自动刷新）

所有需要Token的脚本都支持**自动刷新Token**功能：

- 当接口返回 `401` 或 `418` 状态码时，脚本会自动调用 `login2emu.py` 重新登录
- 自动获取新Token后重试请求
- 用户无需手动处理Token过期问题

**前提**：配置文件中必须保存用户名和密码（首次登录后自动保存）

### 验证登录

调用登录脚本验证账号密码：

```bash
python scripts/login2emu.py --user 用户名 --password 密码
```

- **返回值不是 False**：登录成功，已获取Token，提示用户"已成功登录EMU平台"
- **返回值是 False**：账号或密码错误，提示用户重新输入账号和密码

### Token管理

- 登录成功后，Token和过期时间会自动保存到 `account.config`
- **用户名和密码也会自动保存**，用于Token自动刷新
- 后续操作直接读取配置文件中的Token
- 当Token失效时（返回401/418），脚本会自动调用login2emu.py刷新Token
- 无需每次手动登录

## 功能列表

所有功能通过对应的 Python 脚本实现，脚本位于 `scripts/` 目录。

### 脚本清单

| 脚本 | 功能 | 用法 |
|------|------|------|
| `login2emu.py` | 登录获取Token | `python login2emu.py --user 用户 --password 密码` |
| `get_device_info.py` | 查询设备信息 | `python get_device_info.py --sn 设备SN --cmd 命令类型` |
| `get_alarm_list.py` | 查询告警列表 | `python get_alarm_list.py --sn 设备SN --limit 数量` |
| `get_task_list.py` | 查询工单任务 | `python get_task_list.py --status 6 --page-size 10` |

### cmdType 命令类型

| cmdType | 说明 |
|---------|------|
| `GET_DETAIL_INFO` | 设备基本信息 |
| `GET_WIFI_INFO` | 无线信息 |
| `GET_LAN_PORT_LIST_INFO` | LAN口信息 |
| `GET_RADIO_INFO` | 无线频段信息 |
| `GET_UP_LINK_INFO` | 上联口信息 |
| `GET_UP_AND_DOWN_PON_INFO` | 光功率信息 |
| `GET_DIAGNOSTICS_INFO` | 设备诊断信息 |

后续将陆续添加更多功能脚本...

## 使用示例

### 查询设备基本信息

```bash
cd ~/.openclaw/skills/emu-platform/scripts
python get_device_info.py --sn STAR17604308
```

### 查询无线信息

```bash
python get_device_info.py --sn STAR17604308 --cmd GET_WIFI_INFO
```

### 查询光功率信息

```bash
python get_device_info.py --sn STAR17604308 --cmd GET_UP_AND_DOWN_PON_INFO
```

### 查询告警列表

```bash
# 查询最近20条告警
python get_alarm_list.py --sn STAR17604308

# 查询最近10条告警
python get_alarm_list.py --sn STAR17604308 --limit 10

# 查询严重告警
python get_alarm_list.py --sn STAR17604308 --level 0
```

### 查询工单任务

```bash
# 查询所有工单任务（默认10条）
python get_task_list.py

# 查询失败的任务
python get_task_list.py --status 6

# 查询巡检任务
python get_task_list.py --name "巡检"

# 查询重启类型的任务
python get_task_list.py --task-type 2

# 查询指定创建人的成功任务
python get_task_list.py --created-by lihairui --status 5

# 分页查询
python get_task_list.py --page 1 --page-size 20
```

#### 工单任务查询参数说明

| 参数 | 简写 | 说明 |
|------|------|------|
| `--page` | `-p` | 页码，默认1 |
| `--page-size` | `-s` | 每页数量，默认10 |
| `--category` | `-c` | 工单设备大类 |
| `--name` | `-n` | 工单名称（模糊匹配） |
| `--task-type` | `-t` | 任务类型 |
| `--schedule-strategy` | - | 调度策略 |
| `--created-by` | - | 创建用户 |
| `--status` | - | 任务状态 |

#### 任务类型 (task-type)

| 值 | 说明 |
|----|------|
| 0 | 工作流 |
| 1 | 升级 |
| 2 | 重启 |
| 3 | 抓日志 |
| 4 | shell |
| 5 | 巡检 |
| 6 | 获取日志 |
| 8 | 配置项 |

#### 任务状态 (status)

| 值 | 说明 |
|----|------|
| 0 | 待审批 |
| 1 | 审批中 |
| 2 | 审批不过 |
| 3 | 未开始 |
| 4 | 进行中 |
| 5 | 成功 |
| 6 | 失败 |
| 7 | 终止 |
| 8 | 暂停 |

## 注意事项

- 首次使用需配置 `account.config` 文件
- Token失效需要重新登陆获取
- 该接口为内网接口，需确保网络可达
