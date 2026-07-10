<a id="top"></a>

<div align="center">

# AI Agent

</div>

基于 LangGraph 的本地 Agent 骨架  
支持 Ollama、本地工具、短期记忆和 MCP 外部工具接入

---

## 目录

- [项目简介](#intro)
- [能力概览](#features)
- [快速开始](#quick-start)
  - [1. 进入项目目录](#step-cd)
  - [2. 创建虚拟环境](#step-venv)
  - [3. 激活虚拟环境](#step-activate)
  - [4. 安装依赖](#step-install)
  - [5. 安装 Ollama 并拉取模型](#step-ollama)
  - [6. 准备配置文件](#step-env)
  - [7. 运行 Agent](#step-run)
- [最小命令清单](#commands-min)
- [核心工作流](#workflow)
- [目录结构](#layout)
- [架构分层](#layers)
- [短期记忆](#memory)
- [MCP 工具](#mcp)
- [配置说明](#config)
- [常用命令](#commands)
- [测试](#tests)
- [常见问题](#faq)
- [更多文档](#docs)
- [当前边界](#scope)
- [推荐下一步](#next)

---

<a id="intro"></a>

## 项目简介

这是一个“能跑、好懂、可扩展”的 Agent 基础项目。它先把 Agent 项目最关键的几层拆清楚：

```text
入口 -> 抽象 -> 核心 -> 适配 -> 工具/记忆/数据结构 -> 外部服务
```

你可以把它理解成一个本地 Agent 的起步模板：

```text
用户输入
  -> 大模型推理
  -> 判断是否需要工具
  -> 调用工具
  -> 读取工具结果
  -> 输出最终答案
```

[回到顶部](#top)

---

<a id="features"></a>

## 能力概览

| 项目项 | 当前状态 |
|---|---|
| Agent 框架 | LangGraph |
| 执行策略 | ReAct |
| 默认模型 | Ollama `qwen3:4b` |
| Python 版本 | 推荐 Python 3.12，已验证 3.12.10 |
| 工具系统 | 内置工具 + MCP 工具 |
| 默认工具 | `calculator`、MCP 示例 `add`、`multiply` |
| 记忆能力 | 进程内短期记忆 |
| 默认入口 | `app.py` CLI |
| 配置方式 | `.env` + 环境变量 |

适合用来：

- 跑通一个最小可用的本地 Agent。
- 学习 LangGraph 的 ReAct 流程。
- 使用 Ollama 本地模型。
- 添加自定义内置工具。
- 通过 MCP 接入外部工具。
- 继续扩展长期记忆、搜索、天气、文件工具或 Web API。

[回到顶部](#top)

---

<a id="quick-start"></a>

## 快速开始

下面命令适用于 Windows PowerShell。

<a id="step-cd"></a>

### 1. 进入项目目录

```powershell
cd D:\MyCode\AI-Agent
```

<a id="step-venv"></a>

### 2. 创建虚拟环境

推荐使用 Python 3.12：

```powershell
py -3.12 -m venv .venv
```

如果你的默认 `python` 已经是 3.12，也可以：

```powershell
python -m venv .venv
```

<a id="step-activate"></a>

### 3. 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

激活成功后，命令行前面会出现：

```text
(.venv)
```

<a id="step-install"></a>

### 4. 安装依赖

开发和测试推荐安装：

```powershell
pip install -r requirements-dev.txt
```

只运行项目可以安装：

```powershell
pip install -r requirements.txt
```

`requirements-dev.txt` 已经包含 `requirements.txt`，所以开发时不需要两个都装。

<a id="step-ollama"></a>

### 5. 安装 Ollama 并拉取模型

安装 Ollama 后，拉取默认模型：

```powershell
ollama pull qwen3:4b
```

确认 Ollama 可用：

```powershell
ollama --version
ollama list
```

<a id="step-env"></a>

### 6. 准备配置文件

如果还没有 `.env`：

```powershell
Copy-Item .env.example .env
```

默认配置会使用：

```text
MODEL_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://localhost:11434
```

<a id="step-run"></a>

### 7. 运行 Agent

```powershell
python app.py
```

启动成功后会看到类似输出：

```text
Agent ready: provider=ollama, model=qwen3:4b, tools=3, thread=default
Type 'exit' or 'quit' to stop. Use '/thread NAME' to switch memory thread.
```

可以输入：

```text
2 + 3 * 4 等于多少？
```

退出：

```text
exit
```

[回到顶部](#top)

---

<a id="commands-min"></a>

## 最小命令清单

如果已经安装好 Python 3.12 和 Ollama，可以直接按顺序执行：

```powershell
cd D:\MyCode\AI-Agent
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
ollama pull qwen3:4b
Copy-Item .env.example .env
python app.py
```

[回到顶部](#top)

---

<a id="workflow"></a>

## 核心工作流

这个 Agent 的一次请求大致这样流动：

```text
用户输入
  -> app.py
  -> LangGraphAgent
  -> LangGraph ReAct Graph
  -> LLM 判断是否需要工具
  -> ToolNode 调用工具
  -> LLM 根据工具结果继续推理
  -> AgentResult 最终回答
```

ReAct 策略可以理解为：

```text
Reason -> Act -> Observe -> Reason -> Final Answer
```

也就是说，模型不是一次性回答，而是可以先判断、再调用工具、再根据工具结果回答。

[回到顶部](#top)

---

<a id="layout"></a>

## 目录结构

```text
.
|-- app.py
|-- config.py
|-- interfaces/
|-- core/
|-- adapters/
|-- tools/
|-- memory/
|-- schemas/
|-- examples/
|-- tests/
|-- ARCHITECTURE.md
|-- Agent架构图.puml
`-- README.md
```

| 路径 | 作用 |
|---|---|
| `app.py` | CLI 入口，负责组装模型、工具、记忆和图 |
| `config.py` | 读取 `.env` 和环境变量 |
| `interfaces/` | 定义稳定接口协议 |
| `core/` | Agent 核心门面、状态和策略 |
| `adapters/` | LangGraph、LangChain、MCP 等外部适配 |
| `tools/` | 内置工具，目前有 `calculator` |
| `memory/` | 短期记忆实现和长期记忆预留 |
| `schemas/` | Pydantic 数据结构 |
| `examples/` | 示例 MCP server |
| `tests/` | 单元测试 |
| `ARCHITECTURE.md` | 更详细的代码架构导览 |
| `Agent架构图.puml` | PlantUML 架构图 |

[回到顶部](#top)

---

<a id="layers"></a>

## 架构分层

```text
Application 入口层
  -> Interfaces 抽象层
  -> Core 核心层
  -> Adapters 适配层
  -> Runtime 能力层
  -> External 外部服务
```

| 层 | 对应位置 | 说明 |
|---|---|---|
| Application | `app.py`, `config.py` | 负责启动和组装 |
| Interfaces | `interfaces/` | 定义稳定抽象，减少框架绑定 |
| Core | `core/` | 封装 Agent 行为 |
| Adapters | `adapters/` | 接入 LangGraph、LangChain、MCP、模型后端 |
| Runtime | `tools/`, `memory/`, `schemas/` | 提供工具、记忆和数据结构 |
| External | Ollama、MCP server、API 服务 | 外部模型和工具服务 |

[回到顶部](#top)

---

<a id="memory"></a>

## 短期记忆

短期记忆在：

```text
memory/short_term.py
```

当前使用 LangGraph 的 `InMemorySaver`：

```text
thread_id -> LangGraph config -> InMemorySaver -> messages state
```

同一个 `thread_id` 会保留同一段会话上下文。

在 CLI 中可以切换会话：

```text
/thread project_a
```

注意：这是短期记忆，只在当前 Python 进程中有效。程序退出后不会持久化。

[回到顶部](#top)

---

<a id="mcp"></a>

## MCP 工具

MCP 配置文件是：

```text
mcp_servers.json
```

示例：

```json
{
  "mcpServers": {
    "local_math": {
      "transport": "stdio",
      "command": "python",
      "args": ["examples/mcp_math_server.py"]
    }
  }
}
```

当前示例 MCP server 提供：

```text
add
multiply
```

如果 `mcp_servers.json` 不存在，Agent 不会报错，只会跳过 MCP 工具。

[回到顶部](#top)

---

<a id="config"></a>

## 配置说明

默认 `.env.example`：

```text
MODEL_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://localhost:11434

OPENAI_COMPATIBLE_MODEL=
OPENAI_COMPATIBLE_BASE_URL=
OPENAI_COMPATIBLE_API_KEY=

AGENT_TEMPERATURE=0
AGENT_THREAD_ID=default
MCP_CONFIG_PATH=mcp_servers.json
```

### 切换 Ollama 模型

例如换成更小的模型：

```text
OLLAMA_MODEL=qwen3:1.7b
```

并先拉取：

```powershell
ollama pull qwen3:1.7b
```

### 切换到 OpenAI-compatible API

```text
MODEL_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_MODEL=your-model
OPENAI_COMPATIBLE_BASE_URL=https://your-provider.example/v1
OPENAI_COMPATIBLE_API_KEY=your-api-key
```

注意：不同 OpenAI-compatible 服务的能力不一定完全一致，尤其是工具调用、JSON 输出、上下文长度和流式输出。

[回到顶部](#top)

---

<a id="commands"></a>

## 常用命令

| 目标 | 命令 |
|---|---|
| 激活虚拟环境 | `.\.venv\Scripts\Activate.ps1` |
| 安装开发依赖 | `pip install -r requirements-dev.txt` |
| 运行 Agent | `python app.py` |
| 运行测试 | `python -m pytest -q` |
| 拉取默认模型 | `ollama pull qwen3:4b` |
| 查看 Ollama 模型 | `ollama list` |

[回到顶部](#top)

---

<a id="tests"></a>

## 测试

运行：

```powershell
python -m pytest -q
```

当前测试覆盖：

- calculator 正常计算。
- calculator 拒绝危险表达式。
- 默认配置加载。
- MCP 配置加载。

[回到顶部](#top)

---

<a id="faq"></a>

## 常见问题

### 每次运行都要激活虚拟环境吗？

每次打开新的终端，都建议先激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果命令行前面已经有 `(.venv)`，说明已经激活。

### `requirements-dev.txt` 还需要同时安装 `requirements.txt` 吗？

不需要。

`requirements-dev.txt` 里已经包含：

```text
-r requirements.txt
```

所以执行：

```powershell
pip install -r requirements-dev.txt
```

会自动先安装运行依赖，再安装测试依赖。

### PowerShell 找不到 `ollama`

先检查：

```powershell
ollama --version
```

如果找不到，说明 Ollama 没安装好，或者没有加入 PATH。安装后建议重启 PowerShell。

### 工具数量为什么不是 3？

默认工具包括：

- 内置 `calculator`
- MCP `add`
- MCP `multiply`

如果只看到 1 个工具，一般是 MCP 没有加载。检查：

```text
mcp_servers.json
MCP_CONFIG_PATH
examples/mcp_math_server.py
```

[回到顶部](#top)

---

<a id="docs"></a>

## 更多文档

| 文档 | 用途 |
|---|---|
| `ARCHITECTURE.md` | 快速理解代码结构和分层关系 |
| `Agent架构图.puml` | PlantUML 架构图 |

[回到顶部](#top)

---

<a id="scope"></a>

## 当前边界

已具备：

- CLI Agent
- LangGraph ReAct 图
- Ollama 本地模型接入
- OpenAI-compatible 预留接入
- 短期记忆
- 内置计算器工具
- MCP 工具加载
- 基础测试

暂未实现：

- 长期记忆
- 向量数据库
- Web UI
- HTTP API server
- 真实搜索工具
- 真实天气工具
- 完整 Plan&Execute 策略

[回到顶部](#top)

---

<a id="next"></a>

## 推荐下一步

1. 先跑通 `python app.py`。
2. 用 calculator 验证工具调用。
3. 确认 MCP 的 `add`、`multiply` 可以加载。
4. 再添加你的业务工具。
5. 最后再考虑长期记忆和复杂规划。

[回到顶部](#top)
