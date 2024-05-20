# weather-elf
天气小妖精：一个基于阿里云 LLM 的天气预警提醒小 demo。

## 配置运行
### 启用redis
本项目依赖一个 redis 服务，需要基于 `localhost:6379` 端口启动 redis 服务
```bash
docker run -d --name redis -p 6379:6379 redis
```

### 后端
1. Python3.9 环境
2. 安装依赖：pip install -r requirements.txt
3. 配置通义千问大语言模型 Key：export DASHSCOPE_API_KEY=`<Your sercret key>`([DashScope](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key?spm=a2c4g.11186623.0.0.6d1b12b0ZMRUxQ))
4. 配置彩云天气 API Key: export CAIYUN_API_KEY=`<Your api key>`([彩云天气开放平台](https://platform.caiyunapp.com/login?redirect=/dashboard/index))
5. 启动运行：python app.py

### 前端
1. 安装依赖：npm install
2. 启动服务：npm run serve

## 使用
上述步骤完成后，即可在浏览器中访问 http://localhost:8080/
