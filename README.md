# 上海图书馆开放数据API测试工具

## 动机

上海图书馆提供了丰富地开放数据API，包括古籍、碑帖、电影、地名志等多个领域的数据接口。但是：

- **API众多**：有90多个不同的API接口，手动逐一测试费时费力
- **状态难知**：不知道哪些API正常工作，哪些存在问题

## 这个工具能做什么？

✅ **一键测试所有API** - 自动测试90多个API接口（截至2025年），无需手动操作

✅ **记录错误信息** - 失败的请求会详细记录时间、URL、错误原因等 

## 快速开始

### 1. 准备工作
确保你的电脑已安装Python 3.6+，然后安装依赖：
```bash
pip install -r requirements.txt
```

### 2. 获取API密钥
访问上海图书馆开放数据平台申请API密钥：https://data.library.sh.cn/key

### 3. 配置API密钥
提供两种方式：
1. 将获取到的API密钥设置为电脑的环境变量 `SHANGHAI_LIBRARY_API_KEY`；
2. 修改 `config.py` 文件中的 `API_KEY` 变量，例如：
    ```python
    API_KEY = os.getenv('SHANGHAI_LIBRARY_API_KEY', "[你的API KEY]输入这里")
    ```


### 4. 运行
直接运行即可开始测试所有API：
```bash
python main.py
```

程序会自动：
- 逐个调用每个API接口
- 在终端显示测试进度和结果
- 将成功响应保存到 `api_results/` 文件夹
- 将失败响应写入 `log/error_log.json`

### 5. 查看结果
- **成功的数据**：在 `api_results/` 文件夹中，每个API一个文件
- **错误记录**：在 `log/error_log.json` 中查看失败的API详情

