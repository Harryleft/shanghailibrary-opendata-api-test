# 实时监控功能说明

## 概述

实时监控功能提供了一个基于WebSocket的实时API状态监控仪表板，可以自动定期检查所有API的状态，并实时推送更新到浏览器。

## 功能特性

### 核心功能
- **实时状态监控**: 每30秒自动检查所有API状态
- **WebSocket推送**: 实时将状态更新推送到所有连接的客户端
- **响应时间统计**: 记录每个API的响应时间
- **可视化仪表板**: 现代化的Web界面展示API状态

### 仪表板功能
- **实时状态指示器**: 显示连接状态和最后更新时间
- **统计卡片**: 总API数、在线数、离线数、平均响应时间
- **分类目录**: 按分类浏览API，显示每个分类的健康状态
- **搜索和筛选**: 按名称搜索、按状态筛选、按分类筛选
- **API详情弹窗**: 查看API的详细信息
- **自动刷新**: 可切换的自动刷新功能

### 状态类型
- **在线 (success)**: API返回200状态码
- **离线 (error)**: API返回错误状态码或请求失败
- **超时 (timeout)**: 请求超时（>10秒）

## 安装

### 1. 安装依赖

```bash
# 激活虚拟环境
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# 安装实时监控依赖
pip install -r requirements_realtime.txt
```

### 2. 设置API Key

```bash
# Windows (Command Prompt):
set SHANGHAI_LIBRARY_API_KEY=your_key_here

# Windows (PowerShell):
$env:SHANGHAI_LIBRARY_API_KEY="your_key_here"

# Linux/Mac:
export SHANGHAI_LIBRARY_API_KEY=your_key_here
```

## 使用方法

### 快速启动

#### Windows:
```bash
start_realtime_monitor.bat
```

#### Linux/Mac:
```bash
chmod +x start_realtime_monitor.sh
./start_realtime_monitor.sh
```

#### 手动启动:
```bash
python realtime_server.py
```

### 访问仪表板

服务器启动后，在浏览器中打开:
```
http://localhost:5000
```

## 配置

### 服务器配置 (realtime_server.py)

```python
# API配置
API_KEY = os.environ.get('SHANGHAI_LIBRARY_API_KEY', 'YOUR_API_KEY_HERE')
BASE_URL = 'https://data.library.sh.cn/api'

# 监控配置
CHECK_INTERVAL = 30  # API检查间隔（秒）
MAX_CONCURRENT_CHECKS = 5  # 最大并发检查数
REQUEST_TIMEOUT = 10  # 请求超时（秒）

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000
```

## 工作原理

### 架构

```
┌─────────────────┐
│  浏览器仪表板    │
│  (WebSocket)    │
└────────┬────────┘
         │ WebSocket连接
         │
┌────────▼────────┐
│  Flask服务器     │
│  + WebSocket    │
└────────┬────────┘
         │
         │ 定期检查
         │
┌────────▼────────┐
│  API监控循环     │
│  (后台线程)      │
└─────────────────┘
```

### 数据流

1. **初始化**: 服务器启动，加载API定义
2. **监控循环**: 后台线程定期检查API状态
3. **状态更新**: 检查结果存储在内存中
4. **WebSocket推送**: 状态更新通过WebSocket推送到所有连接的客户端
5. **前端更新**: 浏览器接收更新并刷新界面

### API检查流程

```python
1. 从api_lists.py加载API定义
2. 每30秒执行一次批量检查
3. 每批次最多检查5个API
4. 记录响应时间、状态码、错误信息
5. 更新全局状态
6. 通过WebSocket推送到客户端
```

## API端点

### HTTP端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 仪表板HTML页面 |
| `/data/stats.json` | GET | 获取当前统计数据 |
| `/data/apis` | GET | 获取所有API状态 |

### WebSocket端点

| 端点 | 描述 |
|------|------|
| `/ws` | WebSocket连接端点 |

### WebSocket消息类型

#### 客户端 → 服务器

```json
{
  "type": "ping"
}
```

```json
{
  "type": "refresh"
}
```

#### 服务器 → 客户端

```json
{
  "type": "initial",
  "timestamp": "2026-01-05T10:30:00",
  "total_apis": 91,
  "success_count": 86,
  "error_count": 5,
  "apis": [...]
}
```

```json
{
  "type": "status_update",
  "timestamp": "2026-01-05T10:30:30",
  "total_apis": 91,
  "success_count": 85,
  "error_count": 6,
  "categories": {...}
}
```

```json
{
  "type": "pong"
}
```

## 故障排除

### 问题: WebSocket连接失败

**解决方案**:
1. 检查服务器是否正在运行
2. 检查防火墙设置
3. 确认端口5000未被占用
4. 查看浏览器控制台错误信息

### 问题: API检查超时

**解决方案**:
1. 检查网络连接
2. 增加REQUEST_TIMEOUT值
3. 检查API Key是否有效
4. 减少MAX_CONCURRENT_CHECKS

### 问题: 所有API显示离线

**解决方案**:
1. 确认API Key已正确设置
2. 检查BASE_URL是否正确
3. 手动测试API访问
4. 查看服务器日志

## 性能优化

### 调整检查间隔

```python
# 实时监控（30秒）
CHECK_INTERVAL = 30

# 减少负载（60秒）
CHECK_INTERVAL = 60

# 更频繁的检查（15秒）
CHECK_INTERVAL = 15
```

### 调整并发数

```python
# 默认配置
MAX_CONCURRENT_CHECKS = 5

# 更快的检查（可能增加服务器负载）
MAX_CONCURRENT_CHECKS = 10

# 更温和的检查
MAX_CONCURRENT_CHECKS = 3
```

## 扩展功能

### 添加告警功能

可以在监控循环中添加告警逻辑:

```python
def check_alerts():
    error_rate = error_count / total_apis
    if error_rate > 0.5:
        send_alert(f"高错误率: {error_rate*100}%")
```

### 添加历史数据

可以使用Redis或数据库存储历史数据:

```python
import redis
r = redis.Redis()

def save_to_history(data):
    r.lpush('api:history', json.dumps(data))
    r.ltrim('api:history', 0, 1000)
```

### 添加通知功能

可以集成邮件或Webhook通知:

```python
def send_notification(message):
    # 发送邮件
    send_email(message)

    # 或发送Webhook
    requests.post(WEBHOOK_URL, json={"text": message})
```

## 许可证

与主项目相同
