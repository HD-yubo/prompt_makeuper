# prompt makeuper

基于 FastAPI 的提示词优化服务，通过 LLM 驱动的技能选择与模板优化，自动将模糊的提示词转化为高质量的结构化提示词。

> 📖 [English README](./README.md)

## 工作原理

```
用户输入 → 技能选择 (LLM) → 技能应用 (模板) → 优化后的提示词
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Key 等配置

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 配置

在 `.env` 中填写以下关键配置：

```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1  # 兼容任何 OpenAI 格式的接口
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.7
ENABLE_LOGGING=true
```

支持 OpenAI、Azure OpenAI、Ollama、LM Studio、vLLM 等任意兼容 OpenAI 接口的服务。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/makeup_prompt` | 优化提示词 |
| `GET` | `/skills` | 获取可用技能列表 |
| `GET` | `/health` | 健康检查 |

**调用示例：**
```bash
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "写代码"}'
```

## 技能列表

| 技能 | 适用场景 |
|------|----------|
| **clarity** | 表达不清晰或存在歧义的提示词 |
| **specificity** | 过于笼统或模糊的请求 |
| **structure** | 缺乏组织结构的提示词 |
| **examples** | 需要明确输出格式的提示词 |
| **constraints** | 开放性任务，需要聚焦范围 |
| **mental_model** | 复杂的多步骤任务 |
| **self_verify** | 对结果准确性要求较高的任务 |
| **progressive** | 大型多阶段项目 |

## 项目结构

```
prompt_makeuper/
├── app/
│   ├── main.py            # FastAPI 应用入口
│   ├── config.py          # 配置管理
│   ├── models/            # Pydantic 数据模型
│   └── services/          # LLM 客户端、技能管理、优化器
│       └── skills/templates/  # YAML 技能定义文件
├── extensions/            # Chrome 浏览器扩展
├── docs/                  # 详细文档
├── tests/
└── .env.example
```

## 文档

- [快速上手指南](./docs/QUICKSTART.md)
- [API 文档](./docs/makeup_prompt_api_documentation.md)

## 许可证

MIT
