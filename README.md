# AI Agent

这是一个基于 LangGraph 的最小可运行 Agent 项目。它的目标不是一次性做成完整生产系统，而是先搭出一套清晰、可扩展、能运行的 Agent 骨架。

当前版本支持：

- 使用 LangGraph 实现 ReAct Agent 执行循环。
- 默认使用本地 Ollama 模型 `qwen3:4b`。
- 预留 OpenAI-compatible API 接入方式。
- 使用 `thread_id` 实现进程内短期记忆。
- 内置一个安全的 `calculator` 计算器工具。
- 支持通过 MCP 加载外部工具。
- 使用 `interfaces/`、`core/`、`adapters/` 分层，避免核心逻辑直接绑定具体框架。

## 这个项目是什么

这个项目实现的是一个“可以调用工具的聊天式 Agent”。

普通聊天模型只能根据输入直接生成回答；Agent 则可以在回答前判断是否需要调用工具。例如用户问：

```text
2 + 3 * 4 等于多少？
```

Agent 可以选择调用 `calculator` 工具，拿到工具返回的结果，再把最终答案回复给用户。

第一版的执行策略是 ReAct：

```text
Reason -> Act -> Observe -> Reason -> Final Answer
```

含义是：

- `Reason`：模型判断当前问题应该直接回答，还是需要调用工具。
- `Act`：如果需要工具，Agent 调用对应工具。
- `Observe`：工具返回结果，作为观察信息交还给模型。
- `Reason`：模型基于观察结果继续推理。
- `Final Answer`：模型输出最终答案。

## 适合谁看

如果你不了解这个项目，可以按下面顺序阅读：

1. 先看“核心概念”。
2. 再看“请求是如何流转的”。
3. 然后看“目录结构”。
4. 最后看“安装与运行”和“如何扩展”。

如果你只是想跑起来，直接跳到“安装与运行”。

## 核心概念

### Agent

Agent 是一个可以根据任务自主决定下一步动作的程序。这里的 Agent 可以：

- 接收用户输入。
- 调用大模型推理。
- 判断是否需要工具。
- 调用工具。
- 读取工具结果。
- 继续推理并返回最终答案。

### LangGraph

LangGraph 是本项目的 Agent 流程编排框架。

在这个项目里，LangGraph 负责维护 ReAct 流程：

```text
用户输入 -> agent 节点 -> 是否需要工具 -> tools 节点 -> agent 节点 -> 最终答案
```

### LangChain

LangChain 在这里主要用于统一模型和工具接口。

例如：

- `ChatOllama` 用来连接本地 Ollama 模型。
- `ChatOpenAI` 可以连接 OpenAI-compatible API。
- `@tool` 可以把普通 Python 函数包装成模型可调用工具。

### Ollama

Ollama 用来在本地运行大模型。

当前默认模型是：

```text
qwen3:4b
```

这意味着项目默认不依赖云端 API key，只要本机安装 Ollama 并拉取模型即可运行。

### MCP

MCP 是 Model Context Protocol，可以理解为一种“外部工具接入协议”。

通过 MCP，Agent 不需要把所有工具都写死在项目里，而是可以从外部 MCP server 加载工具。

当前项目已经提供了一个示例 MCP server：

```text
examples/mcp_math_server.py
```

它提供两个工具：

- `add`
- `multiply`

### 短期记忆

短期记忆指的是 Agent 在当前 Python 进程里记住一段会话上下文。

本项目用 LangGraph 的 `InMemorySaver` 实现短期记忆，并用 `thread_id` 区分不同会话。

注意：这是短期记忆，不是长期记忆。程序退出后，记忆会消失。

## 请求是如何流转的

一次用户输入的大致流程如下：

```text
用户在 CLI 输入问题
        |
        v
app.py 读取输入
        |
        v
LangGraphAgent.ainvoke(...)
        |
        v
LangGraph ReAct Graph
        |
        v
LLM 判断是否需要工具
        |
        +-- 不需要工具 -> 直接输出最终答案
        |
        +-- 需要工具 -> 调用 calculator 或 MCP 工具
                            |
                            v
                         工具返回结果
                            |
                            v
                         LLM 继续推理
                            |
                            v
                         输出最终答案
```

短期记忆在这个过程中通过 `thread_id` 生效：

```text
thread_id -> LangGraph config -> InMemorySaver -> messages state
```

同一个 `thread_id` 会复用同一段消息历史，不同 `thread_id` 互相隔离。

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
`-- utils/
```

下面是每个目录的职责。

### `app.py`

项目入口文件。

它负责：

- 读取 `.env` 配置。
- 创建 LLM。
- 创建短期记忆。
- 加载内置工具。
- 加载 MCP 工具。
- 构建 LangGraph 图。
- 启动命令行交互。

如果你想知道整个项目怎么串起来，先看这个文件。

### `config.py`

配置读取模块。

它负责从 `.env` 和系统环境变量中读取配置，例如：

- 使用哪个模型 provider。
- Ollama 模型名。
- Ollama 服务地址。
- OpenAI-compatible API 地址。
- MCP 配置文件路径。
- 默认 `thread_id`。

核心配置类是：

```text
Settings
```

### `interfaces/`

稳定抽象层。

这里定义项目内部最重要的接口协议：

- `Agent`
- `LLMFactory`
- `ToolBindableLLM`
- `ShortTermMemory`
- `Tool`
- `Executor`

设计目的：核心代码尽量依赖这些抽象，而不是直接依赖 LangGraph、LangChain、Ollama 或 MCP。

这样未来替换框架时，不需要大面积改核心逻辑。

### `core/`

Agent 核心层。

当前主要内容：

- `core/agent.py`：提供 `LangGraphAgent`，把编译后的 LangGraph 图包装成统一 Agent 接口。
- `core/state.py`：定义 Agent 状态结构。
- `core/context.py`：定义会话上下文。
- `core/controller.py`：定义执行策略，目前只有 `REACT`。
- `core/reasoning/`：为后续 planner、reflector 等推理模块预留。
- `core/executor/`：为后续自定义执行器预留。

### `adapters/`

外部框架和协议适配层。

它负责把具体框架接进项目，但不让核心层直接依赖外部细节。

当前包括：

- `adapters/langchain/llm.py`：根据配置创建 `ChatOllama` 或 `ChatOpenAI`。
- `adapters/langgraph/graph.py`：构建 ReAct LangGraph 图。
- `adapters/mcp/client.py`：读取 `mcp_servers.json` 并加载 MCP 工具。
- `adapters/openai/`：预留给更复杂的 OpenAI 适配逻辑。

### `tools/`

内置工具目录。

当前实现了：

- `calculator.py`：安全计算基础算术表达式。

保留了：

- `search.py`
- `weather.py`

这两个暂时不实现，因为搜索和天气更适合通过 MCP 或外部 API 接入。

### `memory/`

记忆层。

当前实现：

- `short_term.py`：基于 LangGraph `InMemorySaver` 的短期记忆。

预留：

- `working_memory.py`：工作记忆，适合保存一次运行中的临时结构化数据。
- `long_term.py`：长期记忆，未来可接 SQLite、文件存储或数据库。
- `vector_store.py`：向量记忆，未来可接 embedding 和向量数据库。

### `schemas/`

数据结构层。

这里用 Pydantic 定义稳定数据结构：

- `AgentTask`
- `AgentAction`
- `Observation`
- `Plan`
- `AgentResult`

这些结构让不同层之间的数据传递更清晰。

### `examples/`

示例目录。

当前包含：

```text
examples/mcp_math_server.py
```

这是一个最小 MCP server，用来验证 MCP 工具加载。

### `tests/`

单元测试目录。

当前测试覆盖：

- calculator 表达式计算。
- calculator 拒绝危险 Python 表达式。
- 默认配置加载。
- MCP 配置文件加载。

### `utils/`

通用工具函数预留目录。

当前还没有具体实现。


## 安装与运行

### 1. 安装 Ollama

项目默认使用本地 Ollama，因此需要先安装 Ollama。

安装完成后，在 PowerShell 中确认命令可用：

```powershell
ollama --version
```

### 2. 拉取默认模型

```powershell
ollama pull qwen3:4b
```

如果电脑配置较低，可以换成更小的模型，例如：

```powershell
ollama pull qwen3:1.7b
```

然后修改 `.env`：

```text
OLLAMA_MODEL=qwen3:1.7b
```

### 3. 创建虚拟环境

```powershell
python -m venv .venv
```

### 4. 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. 安装依赖

开发环境建议安装：

```powershell
pip install -r requirements-dev.txt
```

只运行项目可以安装：

```powershell
pip install -r requirements.txt
```

### 6. 创建本地配置

```powershell
Copy-Item .env.example .env
```

当前仓库里也可能已经有一个本地 `.env`。这个文件被 `.gitignore` 忽略，适合保存本机配置。

### 7. 运行 Agent

```powershell
python app.py
```

启动成功后，会看到类似输出：

```text
Agent ready: provider=ollama, model=qwen3:4b, tools=3, thread=default
Type 'exit' or 'quit' to stop. Use '/thread NAME' to switch memory thread.
```

然后可以输入问题：

```text
You> 2 + 3 * 4 等于多少？
```

退出：

```text
exit
```

### 8. 运行测试

```powershell
python -m pytest -q
```

## 配置说明

`.env.example` 中的默认配置：

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

### `MODEL_PROVIDER`

模型后端类型。

当前支持：

```text
ollama
openai_compatible
```

默认：

```text
MODEL_PROVIDER=ollama
```

### `OLLAMA_MODEL`

Ollama 模型名称。

默认：

```text
OLLAMA_MODEL=qwen3:4b
```

### `OLLAMA_BASE_URL`

Ollama 服务地址。

默认：

```text
OLLAMA_BASE_URL=http://localhost:11434
```

### `AGENT_THREAD_ID`

默认短期记忆线程 ID。

默认：

```text
AGENT_THREAD_ID=default
```

### `MCP_CONFIG_PATH`

MCP 配置文件路径。

默认：

```text
MCP_CONFIG_PATH=mcp_servers.json
```

## 切换到 OpenAI-compatible API

如果你要使用兼容 OpenAI API 格式的云端模型，可以这样配置：

```text
MODEL_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_MODEL=your-model
OPENAI_COMPATIBLE_BASE_URL=https://your-provider.example/v1
OPENAI_COMPATIBLE_API_KEY=your-api-key
```

这种方式适合接入支持 OpenAI-compatible 接口的服务。

注意：不同服务虽然接口格式相似，但能力不一定完全一致。工具调用、JSON 输出、上下文长度、流式输出等能力可能存在差异。

## 短期记忆详解

短期记忆文件：

```text
memory/short_term.py
```

核心类：

```text
LangGraphShortTermMemory
```

它内部创建：

```text
InMemorySaver
```

每次调用 Agent 时，都会传入一个 LangGraph config：

```python
{"configurable": {"thread_id": thread_id}}
```

LangGraph 会根据这个 `thread_id` 找到对应的历史状态。

举例：

```text
thread_id = default
```

代表默认会话。

```text
thread_id = project_a
```

代表另一段独立会话。

在 CLI 中切换：

```text
/thread project_a
```

短期记忆适合：

- 当前命令行会话中的多轮对话。
- 临时上下文。
- 本地开发和调试。

短期记忆不适合：

- 跨进程保存记忆。
- 长期用户画像。
- 大规模知识库检索。

这些能力应该在后续通过长期记忆或向量记忆实现。

## MCP 详解

MCP 配置文件默认是：

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

这个配置表示：

- 启动一个名为 `local_math` 的 MCP server。
- 使用 `stdio` 通信。
- 用 Python 运行 `examples/mcp_math_server.py`。
- 从这个 server 加载可用工具。

当前示例 MCP server 提供：

```text
add
multiply
```

启动 Agent 时，MCP loader 会自动读取配置并加载工具。

如果 `mcp_servers.json` 不存在：

- Agent 不会报错。
- MCP 工具数量为 0。
- 内置工具仍然可用。

## 如何新增一个内置工具

以内置工具为例，可以在 `tools/` 中新增一个文件。

例如新增：

```text
tools/time_tool.py
```

工具函数可以使用 LangChain 的 `@tool`：

```python
from langchain_core.tools import tool


@tool
def current_time() -> str:
    """Return current time."""
    return "..."
```

然后在 `app.py` 中导入并加入工具列表：

```python
from tools.time_tool import current_time

tools = [calculator, current_time, *mcp_bundle.tools]
```

如果工具依赖外部系统，优先考虑通过 MCP 接入，这样核心项目更干净。

## 如何新增一个模型后端

模型创建逻辑在：

```text
adapters/langchain/llm.py
```

当前支持：

- Ollama：`ChatOllama`
- OpenAI-compatible：`ChatOpenAI`

如果要新增一个 provider，一般步骤是：

1. 在 `config.py` 中增加 provider 名称和配置项。
2. 在 `create_chat_model` 中增加分支。
3. 返回一个 LangChain `BaseChatModel` 兼容对象。
4. 确认该模型是否支持工具调用。

如果模型不支持工具调用，ReAct Agent 可能无法正常调用工具。

## 如何扩展长期记忆

长期记忆还没有实现，但目录已经预留：

```text
memory/long_term.py
memory/vector_store.py
```

常见扩展方式：

- SQLite：保存长期会话摘要。
- JSON/Markdown 文件：适合简单本地记忆。
- 向量数据库：适合语义检索和知识库。
- 外部数据库：适合多用户或服务端部署。

推荐路线：

1. 先保留当前短期记忆。
2. 增加长期记忆接口。
3. 每轮对话结束后写入摘要或事实。
4. 下一轮对话开始前检索相关记忆。
5. 把检索结果注入 system prompt 或上下文。

## 当前依赖

运行依赖在：

```text
requirements.txt
```

开发依赖在：

```text
requirements-dev.txt
```

核心依赖包括：

- `langgraph`
- `langchain`
- `langchain-core`
- `langchain-ollama`
- `langchain-openai`
- `langchain-mcp-adapters`
- `mcp`
- `pydantic`
- `python-dotenv`

测试依赖：

- `pytest`

## 当前验证状态

当前项目已验证：

```text
pytest: 5 passed
compileall: passed
MCP example tools: add, multiply loaded
LangGraph graph: compiled successfully
```

## 常见问题

### PowerShell 提示找不到 `ollama`

说明 Ollama 没有安装，或者没有加入系统 PATH。

可以先执行：

```powershell
ollama --version
```

如果仍然找不到，请重新安装 Ollama，或者重启 PowerShell。

### 运行 Agent 时提示模型不存在

需要先拉取模型：

```powershell
ollama pull qwen3:4b
```

### 工具数量不是 3

默认情况下工具包括：

- 内置 `calculator`
- MCP `add`
- MCP `multiply`

如果工具数量是 1，通常表示 MCP 没有加载。检查：

```text
mcp_servers.json
MCP_CONFIG_PATH
examples/mcp_math_server.py
```

### 为什么短期记忆重启后消失

因为当前使用的是 `InMemorySaver`，它只保存在当前进程内。

如果需要重启后仍然保留，需要实现长期记忆。

### 为什么要有 `interfaces/`

因为 Agent 项目后续很容易更换模型、工具协议、执行框架。

`interfaces/` 的作用是稳定核心契约，让核心代码不被具体框架绑死。

### 为什么不直接把所有逻辑写在 `app.py`

小 demo 可以这样写，但后续会很难扩展。

当前分层的好处是：

- 模型后端可以替换。
- 工具来源可以替换。
- 记忆策略可以替换。
- 执行策略可以替换。
- 测试更容易写。

## 后续可扩展方向

可以继续扩展：

- Plan&Execute 策略。
- Hybrid 策略：轻量规划 + ReAct 执行 + 反思。
- 长期记忆。
- 向量检索记忆。
- Web 搜索 MCP 工具。
- 天气 MCP 工具。
- 文件读写工具。
- 更完整的 CLI 参数。
- Web UI 或 API server。

建议优先顺序：

1. 先跑通 Ollama + ReAct + calculator。
2. 再确认 MCP 工具加载稳定。
3. 然后增加真实业务工具。
4. 最后再加长期记忆和复杂规划。
