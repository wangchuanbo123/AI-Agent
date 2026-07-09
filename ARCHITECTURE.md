# 项目架构速览

这份文档用于快速理解当前 Agent 项目的代码结构。它比 README 更偏“代码导览”：告诉你每一层做什么、每个文件夹放什么、一次请求如何流转，以及后续想改功能应该从哪里入手。

## 一句话理解这个项目

这是一个基于 LangGraph 的本地 Agent 骨架：

```text
用户输入 -> Agent 推理 -> 必要时调用工具 -> 读取工具结果 -> 输出最终答案
```

当前默认模型是本地 Ollama：

```text
qwen3:4b
```

当前默认执行策略是 ReAct：

```text
Reason -> Act -> Observe -> Reason -> Final Answer
```

## 最重要的三个问题

### 1. 入口在哪里？

入口是：

```text
app.py
```

它负责把配置、模型、记忆、工具、MCP 和 LangGraph 图组装起来，然后启动 CLI。

### 2. Agent 核心在哪里？

核心门面在：

```text
core/agent.py
```

这里的 `LangGraphAgent` 负责调用编译后的 LangGraph 图，并把最终结果包装成 `AgentResult`。

### 3. LangGraph 流程在哪里？

图构建逻辑在：

```text
adapters/langgraph/graph.py
```

这里定义了 ReAct 图：

```text
START -> agent -> tools_condition
tools_condition -> tools -> agent
tools_condition -> END
```

## 分层架构

项目可以按 6 层理解：

```text
Application 入口层
    |
Interfaces 抽象层
    |
Core 核心层
    |
Adapters 适配层
    |
Runtime 能力层
    |
External 外部服务
```

更贴近代码的关系是：

```text
app.py
  |
  |-- config.py
  |-- interfaces/
  |-- core/
  |-- adapters/
  |-- tools/
  |-- memory/
  `-- schemas/
```

## 各层和文件夹关系

| 架构层 | 对应文件夹/文件 | 主要职责 |
|---|---|---|
| Application 入口层 | `app.py`, `config.py` | 启动程序、读取配置、组装所有组件 |
| Interfaces 抽象层 | `interfaces/` | 定义 Agent、LLM、Tool、Memory、Executor 的稳定协议 |
| Core 核心层 | `core/` | 包装 Agent 行为、状态、上下文和执行策略 |
| Adapters 适配层 | `adapters/` | 接入 LangGraph、LangChain、Ollama、OpenAI-compatible、MCP |
| Runtime 能力层 | `tools/`, `memory/`, `schemas/` | 提供工具、记忆实现和数据结构 |
| Examples/Tests | `examples/`, `tests/` | 示例 MCP server 和单元测试 |
| External 外部服务 | Ollama, MCP server, OpenAI-compatible API | 真正的模型服务和外部工具服务 |

## 一次请求的完整流转

用户在 CLI 输入问题后，请求大致这样流动：

```text
1. app.py 读取用户输入
2. app.py 调用 LangGraphAgent.ainvoke(...)
3. LangGraphAgent 把用户消息交给 CompiledStateGraph
4. LangGraph 的 agent_node 调用 LLM
5. LLM 判断是否需要工具
6. 如果不需要工具，直接返回最终答案
7. 如果需要工具，tools_condition 路由到 ToolNode
8. ToolNode 调用 calculator 或 MCP 工具
9. 工具结果作为 Observation 回到 LLM
10. LLM 继续推理并输出最终答案
```

可以简化成：

```text
User
  -> app.py
  -> core/LangGraphAgent
  -> adapters/langgraph/ReAct Graph
  -> adapters/langchain/LLM
  -> tools 或 MCP tools
  -> AgentResult
```

## 根目录文件说明

### `app.py`

项目运行入口。

它做这些事：

- 读取 `.env` 配置。
- 创建短期记忆。
- 创建模型。
- 加载内置工具。
- 加载 MCP 工具。
- 构建 LangGraph 图。
- 启动命令行交互。

看懂 `app.py`，基本就能知道项目如何启动。

### `config.py`

配置模块。

核心类是：

```text
Settings
```

它从 `.env` 和环境变量读取：

- `MODEL_PROVIDER`
- `OLLAMA_MODEL`
- `OLLAMA_BASE_URL`
- `OPENAI_COMPATIBLE_*`
- `AGENT_THREAD_ID`
- `MCP_CONFIG_PATH`

### `requirements.txt`

运行项目需要的依赖。

包括：

- LangGraph
- LangChain
- Ollama adapter
- OpenAI adapter
- MCP adapter
- Pydantic
- dotenv

### `requirements-dev.txt`

开发和测试依赖。

当前主要增加：

```text
pytest
```

### `.env.example`

配置模板。

新环境中可以复制成：

```powershell
Copy-Item .env.example .env
```

### `mcp_servers.json`

本地 MCP server 配置。

当前指向：

```text
examples/mcp_math_server.py
```

用于加载示例 MCP 工具 `add` 和 `multiply`。

### `Agent架构图.puml`

PlantUML 架构图。

适合用来从图形角度理解项目分层。

## `interfaces/`：稳定抽象层

这个目录定义“项目内部承诺使用什么接口”。

它不是具体实现，而是约定。

| 文件 | 作用 |
|---|---|
| `agent.py` | 定义 Agent 应该具备的 `ainvoke` 调用接口 |
| `llm.py` | 定义模型工厂和可绑定工具的 LLM 能力 |
| `memory.py` | 定义短期记忆如何根据 `thread_id` 生成配置 |
| `tool.py` | 定义工具最小协议 |
| `executor.py` | 定义执行器协议 |

为什么需要这一层？

因为以后你可能要换：

- LangGraph -> 其他 Agent 框架
- Ollama -> 云端模型
- 本地工具 -> MCP 工具
- 短期记忆 -> 长期记忆

有 `interfaces/` 之后，核心代码可以少依赖具体框架。

## `core/`：Agent 核心层

这个目录放 Agent 本身的核心概念。

| 文件/目录 | 作用 |
|---|---|
| `agent.py` | 定义 `LangGraphAgent`，把 LangGraph 图包装成统一 Agent |
| `state.py` | 定义图里流转的消息状态 |
| `context.py` | 定义会话上下文 |
| `controller.py` | 定义执行策略，目前是 `REACT` |
| `reasoning/` | 预留 planner、reflector 等推理组件 |
| `executor/` | 预留自定义执行器 |

当前真正关键的是：

```text
core/agent.py
```

它不直接创建模型，不直接加载工具，只负责调用已经组装好的 graph。

## `adapters/`：框架和协议适配层

这个目录负责“接外部世界”。

外部世界包括：

- LangGraph
- LangChain
- Ollama
- OpenAI-compatible API
- MCP

### `adapters/langgraph/`

负责 LangGraph 图编排。

关键文件：

```text
adapters/langgraph/graph.py
```

里面的核心函数：

```text
build_react_graph(...)
```

它负责创建：

- `agent` 节点
- `tools` 节点
- `tools_condition` 条件边
- graph checkpoint

### `adapters/langchain/`

负责创建模型。

关键文件：

```text
adapters/langchain/llm.py
```

核心函数：

```text
create_chat_model(settings)
```

根据配置返回：

- `ChatOllama`
- 或 `ChatOpenAI`

### `adapters/mcp/`

负责加载 MCP 工具。

关键文件：

```text
adapters/mcp/client.py
```

它会读取：

```text
mcp_servers.json
```

然后通过 `MultiServerMCPClient` 加载工具。

如果配置文件不存在，MCP 会被自动跳过，Agent 仍然可以运行。

### `adapters/openai/`

当前只是预留目录。

OpenAI-compatible 模型暂时通过：

```text
adapters/langchain/llm.py
```

创建。

## `tools/`：内置工具层

这个目录放项目自带工具。

| 文件 | 作用 |
|---|---|
| `calculator.py` | 已实现：安全计算基础算术表达式 |
| `search.py` | 占位：后续可接搜索工具 |
| `weather.py` | 占位：后续可接天气工具 |

当前 `calculator` 是第一个可用工具。

它使用 LangChain 的 `@tool` 包装，因此 LangGraph 的 `ToolNode` 可以直接调用它。

## `memory/`：记忆层

这个目录放记忆相关实现。

| 文件 | 作用 |
|---|---|
| `short_term.py` | 已实现：基于 LangGraph `InMemorySaver` 的短期记忆 |
| `working_memory.py` | 预留：工作记忆 |
| `long_term.py` | 预留：长期记忆 |
| `vector_store.py` | 预留：向量记忆 |

当前真正生效的是：

```text
memory/short_term.py
```

短期记忆依赖：

```text
thread_id
```

同一个 `thread_id` 会保留同一段会话上下文。

## `schemas/`：数据结构层

这个目录放统一的数据结构。

| 文件 | 作用 |
|---|---|
| `task.py` | 用户任务输入结构 |
| `action.py` | 工具动作结构 |
| `observation.py` | 工具观察结果结构 |
| `result.py` | Agent 最终返回结果 |
| `plan.py` | 计划结构，后续 Plan&Execute 使用 |

这些 schema 的作用是让不同层之间的数据更清楚。

## `examples/`：示例层

当前只有一个示例：

```text
examples/mcp_math_server.py
```

它是一个很小的 MCP server，暴露两个工具：

```text
add
multiply
```

用于验证 MCP 接入是否正常。

## `tests/`：测试层

当前测试覆盖：

| 文件 | 测试内容 |
|---|---|
| `test_calculator.py` | 计算器正确计算，且拒绝危险表达式 |
| `test_config.py` | 默认配置是否正确 |
| `test_mcp_config.py` | MCP 配置加载是否正确 |

运行：

```powershell
python -m pytest -q
```

## `utils/`：工具函数预留层

当前没有实际逻辑。

以后如果有多个模块都会用到的纯辅助函数，可以放这里。

例如：

- 日志格式化
- 通用文本处理
- 路径处理
- 时间处理

## 代码阅读建议

如果你是第一次看这个项目，建议按这个顺序读：

```text
1. README.md
2. ARCHITECTURE.md
3. app.py
4. config.py
5. adapters/langgraph/graph.py
6. adapters/langchain/llm.py
7. memory/short_term.py
8. tools/calculator.py
9. adapters/mcp/client.py
10. core/agent.py
```

如果只想快速理解运行链路，可以看：

```text
app.py -> adapters/langgraph/graph.py -> core/agent.py
```

## 想新增功能时看哪里

### 新增一个内置工具

看：

```text
tools/calculator.py
app.py
```

做法：

1. 在 `tools/` 新建工具文件。
2. 用 `@tool` 包装函数。
3. 在 `app.py` 中加入工具列表。

### 新增一个 MCP 工具

看：

```text
mcp_servers.json
examples/mcp_math_server.py
adapters/mcp/client.py
```

做法：

1. 准备 MCP server。
2. 在 `mcp_servers.json` 中配置 server。
3. 启动 Agent，MCP 工具会自动加载。

### 更换模型

看：

```text
.env
config.py
adapters/langchain/llm.py
```

如果仍然用 Ollama，只改：

```text
OLLAMA_MODEL=模型名
```

如果用 OpenAI-compatible API，需要改：

```text
MODEL_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_MODEL=...
OPENAI_COMPATIBLE_BASE_URL=...
OPENAI_COMPATIBLE_API_KEY=...
```

### 增加长期记忆

看：

```text
memory/long_term.py
memory/vector_store.py
interfaces/memory.py
```

推荐思路：

1. 保留当前短期记忆。
2. 增加长期记忆接口。
3. 每轮对话后写入摘要或事实。
4. 下一轮对话前检索相关记忆。
5. 把检索结果加入上下文。

### 增加 Plan&Execute

看：

```text
core/controller.py
core/reasoning/
schemas/plan.py
adapters/langgraph/graph.py
```

当前第一版只做 ReAct，Plan&Execute 还没有接入主流程。

## 当前项目边界

当前已经有：

- 可运行 CLI。
- LangGraph ReAct 图。
- Ollama 模型接入。
- OpenAI-compatible 预留接入。
- 短期记忆。
- 内置 calculator 工具。
- MCP 工具加载。
- MCP 示例 server。
- 基础测试。

当前还没有：

- 长期记忆。
- 向量数据库。
- Web UI。
- HTTP API server。
- 真正的搜索工具。
- 真正的天气工具。
- 完整 Plan&Execute。
- 生产级日志和监控。

## 最小运行命令

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

如果是全新环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
ollama pull qwen3:4b
python app.py
```

## 总结

这个项目的核心思路是：

```text
核心逻辑保持简单
外部框架放进 adapters
工具和记忆放进 runtime 层
接口协议放进 interfaces
数据结构放进 schemas
```

所以你可以把它理解成一个“可扩展 Agent 骨架”：

```text
app.py 负责组装
core/ 负责 Agent 门面
adapters/ 负责接框架
tools/ 负责工具
memory/ 负责记忆
schemas/ 负责数据结构
interfaces/ 负责稳定抽象
```
