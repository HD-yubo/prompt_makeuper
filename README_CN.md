# prompt makeuper

基于 FastAPI 的提示词优化服务，通过 LLM 驱动的技能选择与优化，提升提示词质量。

> 📖 [English README](./README.md)

## 工作原理

```
用户输入 → Flash 模型选择技能 → 懒加载技能内容 → 应用技能模板 → 优化后的提示词
```

## 快速开始

- 8 个预定义技能，以标准 `SKILL.md` 文件存储
- **Flash 模型选择技能**（失败时回退主模型）
- **渐进式技能加载**：启动时仅索引 frontmatter，按需懒加载完整技能内容
- **兼容 OpenAI 接口**：支持 OpenAI、Azure OpenAI、Ollama、LM Studio、vLLM 等
- **异步 FastAPI 服务 + CLI 访问**
- **LLM 交互日志记录**，便于调试与分析
- **Chrome 浏览器扩展**集成

## 安装

```bash
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env` 填写 API 配置，然后启动服务：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 配置

在 `.env` 中填写以下关键配置：

```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 可选：Flash 模型用于快速技能选择
# 未设置时自动回退到 OPENAI_* 配置
FLASH_API_KEY=your-flash-api-key-here
FLASH_BASE_URL=https://api.openai.com/v1
FLASH_MODEL=gpt-4o-mini

TEMPERATURE=0.7
ENABLE_LOGGING=true
```

本地模型示例：

```bash
# Ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama2

# LM Studio
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=local-model

# vLLM
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=empty
OPENAI_MODEL=meta-llama/Llama-2-7b
```

## 命令行用法

不启动 HTTP 服务，直接在命令行优化提示词：

```bash
python -m app.cli "写代码"
python -m app.cli "写代码" --output-type xml
python -m app.cli "写代码" --skill structure
python -m app.cli --list-skills
python -m app.cli --file prompt.txt
cat prompt.txt | python -m app.cli
python -m app.cli "写代码" --json
./prompt-makeuper "写代码"
./prompt-makeuper --list-skills
```

CLI 默认只输出优化后的提示词。使用 `--json` 可打印完整结果。
使用 `--skill <名称>` 可跳过自动选择，直接指定技能。
使用 `--list-skills` 或 `--help` 可查看所有可用技能及一句话描述。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/makeup_prompt` | 优化提示词 |
| `GET` | `/skills` | 列出可用技能 |
| `GET` | `/health` | 健康检查 |

**调用示例：**

```bash
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "写代码"}'
```

## 技能列表

| 技能 | 描述 | 适用场景 |
|-------|-------|----------|
| **clarity** | 消除歧义，重组逻辑流程 | 不清晰或混乱的提示词 |
| **specificity** | 增加细节、约束条件与上下文 | 模糊或笼统的请求 |
| **structure** | 用清晰章节和格式组织内容 | 缺乏结构的提示词 |
| **examples** | 包含相关示例以明确预期 | 需要明确输出格式的提示词 |
| **constraints** | 定义输出格式与边界 | 需要聚焦范围的开放性任务 |
| **mental_model** | 挖掘隐含目标，对齐心智模型 | 复杂的多步骤任务 |
| **self_verify** | 添加验证检查点与错误处理 | 对结果准确性要求较高的任务 |
| **progressive** | 将复杂提示词拆解为渐进步骤 | 大型多阶段项目 |

## 项目结构

```
prompt_makeuper/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── cli.py
│   ├── models/
│   ├── services/
│   │   ├── llm_client.py
│   │   ├── skill_manager.py
│   │   ├── skill_parser.py
│   │   └── optimizer.py
│   └── skills/
│       └── <技能名>/SKILL.md
├── docs/
├── extensions/
├── tests/
├── prompt-makeuper
├── requirements.txt
├── .env.example
├── README.md
└── README_CN.md
```

## LLM 交互日志

服务会自动将所有 LLM 交互记录为 JSON 格式，存储在 `logs/YYYYMMDD.log`：

```json
{
  "timestamp": "2026-03-02T10:30:45.123456",
  "stage": "skill_application",
  "metadata": {
    "skill_name": "clarity",
    "iteration": 1
  },
  "input": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "output": "优化后的提示词..."
}
```

查看日志：

```bash
# 查看今日日志
cat logs/$(date +%Y%m%d).log | jq

# 搜索特定技能
cat logs/20260302.log | jq 'select(.metadata.skill_name == "clarity")'

# 统计技能使用次数
cat logs/*.log | jq -r '.metadata.skill_name' | sort | uniq -c
```

## 测试

```bash
pytest
pytest --cov=app tests/
```

## 文档

- [快速上手指南](./docs/QUICKSTART.md)
- [API 文档](./docs/makeup_prompt_api_documentation.md)
- [Embedding 选择器报告](./docs/EMBEDDING_SELECTOR_REPORT.md) - 先前实现的历史笔记

## 许可证

MIT
