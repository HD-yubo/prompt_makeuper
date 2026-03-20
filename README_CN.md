# prompt makeuper

基于 FastAPI 的提示词优化服务，通过嵌入向量技能选择与模板优化，自动将模糊的提示词转化为高质量的结构化提示词。

> 📖 [English README](./README.md)

## 工作原理

```
用户输入 → 技能选择（嵌入向量 / LLM） → 技能应用（模板） → 优化后的提示词
```

优化器执行两阶段流水线：

1. **技能选择** — 通过语义相似度（嵌入向量，快速且无额外费用）将输入提示词匹配至最合适的优化技能。当嵌入向量不可用时，自动回退到 LLM 选择。
2. **技能应用** — 使用所选技能的提示词模板，将输入改写为结构清晰、质量高的提示词。

附加处理步骤：
- **语言检测** — 自动识别输入语言（英文、中文、日文、韩文），并指示 LLM 以相同语言输出。
- **日期过滤** — 将提示词中具体的绝对日期替换为模糊表述，使提示词更具通用性。

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
MAX_ITERATIONS=3
ENABLE_LOGGING=true
LOG_DIR=logs
LOG_LEVEL=INFO
```

支持 OpenAI、Azure OpenAI、Ollama、LM Studio、vLLM 等任意兼容 OpenAI 接口的服务。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/makeup_prompt` | 优化提示词 |
| `GET` | `/skills` | 获取可用技能列表 |
| `GET` | `/health` | 健康检查 |

### 请求参数

```json
{
  "input_prompt": "写代码",
  "output_type": "markdown"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `input_prompt` | string | ✅ | 需要优化的提示词 |
| `output_type` | string | ❌ | 输出格式：`"markdown"`（默认）或 `"xml"` |

### 响应格式

```json
{
  "output_prompt": "## 任务\n编写一个 Python 函数...",
  "skill_used": "specificity",
  "iterations": 1
}
```

### 调用示例

```bash
# Markdown 输出（默认）
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "写代码"}'

# XML 输出
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "写代码", "output_type": "xml"}'
```

## 技能列表

技能以 YAML 模板文件定义，存放于 `app/skills/templates/`。每个技能专注于不同类型的提示词改进。

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

### 新增技能

在 `app/skills/templates/` 中创建新的 YAML 文件即可：

```yaml
name: your_skill
description: 该技能改善的内容

system_prompt: |
  你是一位擅长...的专家。
  只返回改写后的提示词。

optimization_prompt: |
  原始提示词：{input_prompt}

  请将此提示词改写为...
```

无需修改任何代码 — 重启服务后即可使用新技能。

## 多语言支持

服务自动检测输入语言，并指示 LLM 以相同语言输出结果：

| 语言 | 检测依据 |
|------|----------|
| 英文 | ASCII 字符 |
| 中文（简体） | Unicode 范围 `U+4E00–U+9FFF` |
| 日文 | 平假名 / 片假名 Unicode 范围 |
| 韩文 | 谚文 Unicode 范围 |

## 项目结构

```
prompt_makeuper/
├── app/
│   ├── main.py                    # FastAPI 应用入口及路由
│   ├── config.py                  # 基于 pydantic-settings 的配置管理
│   ├── models/
│   │   └── schemas.py             # Pydantic 请求/响应模型
│   ├── services/
│   │   ├── llm_client.py          # OpenAI 兼容 API 客户端
│   │   ├── skill_manager.py       # 技能加载与选择提示词生成
│   │   ├── optimizer.py           # 两阶段优化流水线
│   │   ├── embedding_selector.py  # 基于嵌入向量的技能选择器
│   │   ├── formatter.py           # 输出格式指令生成
│   │   ├── date_filter.py         # 日期模糊化后处理
│   │   └── llm_logger.py          # 请求/响应日志记录
│   └── skills/
│       └── templates/             # YAML 技能定义（8 个内置技能）
├── extensions/                    # Chrome 浏览器扩展（侧边栏 UI）
├── examples/                      # 使用示例
├── tests/                         # Pytest 测试套件
├── requirements.txt
└── .env.example
```

## Chrome 扩展

`extensions/` 目录中包含一个 Chrome 侧边栏扩展，可在浏览器中直接调用后端服务优化提示词。

安装与使用说明请参阅 [extensions/README.md](./extensions/README.md)。

## 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率运行
pytest --cov=app tests/
```

## 许可证

MIT
