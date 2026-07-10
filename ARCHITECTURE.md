<a id="top"></a>

# 架构导览

> README 负责告诉你“怎么安装和运行”。这份文档负责告诉你“代码为什么这样分层，以及应该从哪里读起”。

---

## 目录

- [心智模型](#mental-model)
- [总体流程图](#flow)
- [分层总览](#layers)
- [入口层](#application)
  - [`app.py`](#app-py)
  - [`config.py`](#config-py)
- [抽象层：`interfaces/`](#interfaces)
- [核心层：`core/`](#core)
- [适配层：`adapters/`](#adapters)
  - [`adapters/langgraph/`](#adapter-langgraph)
  - [`adapters/langchain/`](#adapter-langchain)
  - [`adapters/mcp/`](#adapter-mcp)
  - [`adapters/openai/`](#adapter-openai)
- [能力层：工具、记忆、数据结构](#runtime)
  - [`tools/`](#tools)
  - [`memory/`](#memory)
  - [`schemas/`](#schemas)
- [示例和测试](#examples-tests)
- [推荐阅读顺序](#reading)
- [修改功能时看哪里](#change-map)
- [当前项目边界](#scope)
- [架构原则](#principles)
- [配套架构图](#diagram)

---

<a id="mental-model"></a>

## 心智模型

这个项目可以简单理解为：

```text
app.py 负责组装
core/ 负责 Agent 门面
adapters/ 负责接框架和外部协议
tools/ 负责工具
memory/ 负责记忆
schemas/ 负责数据结构
interfaces/ 负责稳定抽象
```

也就是：

```text
入口层 -> 抽象层 -> 核心层 -> 适配层 -> 能力层 -> 外部服务
```

[回到顶部](#top)

---

<a id="flow"></a>

## 总体流程图

```text
User
  |
  v
app.py
  |
  +-- config.py
  +-- memory/short_term.py
  +-- adapters/langchain/llm.py
  +-- adapters/mcp/client.py
  |
  v
adapters/langgraph/graph.py
  |
  v
core/agent.py
  |
  v
AgentResult
```

更细一点的运行链路：

```text
用户输入
  -> app.py
  -> LangGraphAgent.ainvoke(...)
  -> CompiledStateGraph
  -> agent_node 调用 LLM
  -> tools_condition 判断是否需要工具
  -> ToolNode 调用 calculator 或 MCP tools
  -> 工具结果回到 LLM
  -> 输出最终答案
```

[回到顶部](#top)

---

<a id="layers"></a>

## 分层总览

| 层 | 位置 | 解决的问题 |
|---|---|---|
| Application | `app.py`, `config.py` | 程序如何启动，运行时组件如何组装 |
| Interfaces | `interfaces/` | 各组件之间遵守什么契约 |
| Core | `core/` | Agent 对外表现成什么样 |
| Adapters | `adapters/` | 如何接入 LangGraph、LangChain、MCP、模型后端 |
| Runtime | `tools/`, `memory/`, `schemas/` | Agent 能调用什么、记住什么、传递什么数据 |
| Examples | `examples/` | 如何写一个外部 MCP server |
| Tests | `tests/` | 如何验证关键功能 |

[回到顶部](#top)

---

<a id="application"></a>

## 入口层

<a id="app-py"></a>

### `app.py`

这是项目入口。它的职责是“组装”，不是写复杂业务逻辑。

它会按顺序做这些事：

```text
1. 读取 Settings
2. 创建短期记忆
3. 创建聊天模型
4. 加载 MCP 工具
5. 合并内置工具和 MCP 工具
6. 构建 LangGraph ReAct 图
7. 包装成 LangGraphAgent
8. 启动 CLI 循环
```

你想看项目怎么跑起来，就先看 `app.py`。

<a id="config-py"></a>

### `config.py`

这里定义 `Settings`，集中管理配置。

| 配置 | 作用 |
|---|---|
| `MODEL_PROVIDER` | 模型提供方，默认 `ollama` |
| `OLLAMA_MODEL` | Ollama 模型名，默认 `qwen3:4b` |
| `OLLAMA_BASE_URL` | Ollama 服务地址 |
| `OPENAI_COMPATIBLE_*` | OpenAI-compatible API 配置 |
| `AGENT_THREAD_ID` | 默认短期记忆线程 |
| `MCP_CONFIG_PATH` | MCP 配置文件路径 |

[回到顶部](#top)

---

<a id="interfaces"></a>

## 抽象层：`interfaces/`

这一层定义“项目内部希望各组件长什么样”。

| 文件 | 定义 | 说明 |
|---|---|---|
| `agent.py` | `Agent` | Agent 统一调用接口 |
| `llm.py` | `LLMFactory`, `ToolBindableLLM` | 模型创建和工具绑定能力 |
| `memory.py` | `ShortTermMemory` | 短期记忆契约 |
| `tool.py` | `Tool` | 工具最小协议 |
| `executor.py` | `Executor` | 动作执行器契约 |

这一层的价值是：以后换框架、换模型、换工具系统时，核心逻辑不需要跟着大改。

[回到顶部](#top)

---

<a id="core"></a>

## 核心层：`core/`

这一层放 Agent 的核心概念。

| 文件/目录 | 作用 |
|---|---|
| `agent.py` | `LangGraphAgent`，把图包装成统一 Agent |
| `state.py` | 图中流转的消息状态 |
| `context.py` | 会话上下文 |
| `controller.py` | 执行策略枚举，目前是 `REACT` |
| `reasoning/` | 规划、反思等未来能力预留 |
| `executor/` | 自定义执行器预留 |

当前最重要的是：

```text
core/agent.py
```

它只做一件事：调用已经编译好的 LangGraph 图，并提取最后的 AI 回复。

[回到顶部](#top)

---

<a id="adapters"></a>

## 适配层：`adapters/`

这一层负责“和外部框架打交道”。

<a id="adapter-langgraph"></a>

### `adapters/langgraph/`

核心文件：

```text
adapters/langgraph/graph.py
```

核心函数：

```text
build_react_graph(...)
```

它构建 ReAct 图：

```text
START
  -> agent
  -> tools_condition
      -> tools
      -> agent
      -> END
```

| 组件 | 作用 |
|---|---|
| `agent_node` | 调用 LLM 推理 |
| `tools_condition` | 判断模型是否发起工具调用 |
| `ToolNode` | 执行工具 |
| `checkpointer` | 接入短期记忆 |

<a id="adapter-langchain"></a>

### `adapters/langchain/`

核心文件：

```text
adapters/langchain/llm.py
```

核心函数：

```text
create_chat_model(settings)
```

| provider | 返回模型 |
|---|---|
| `ollama` | `ChatOllama` |
| `openai_compatible` | `ChatOpenAI` |

<a id="adapter-mcp"></a>

### `adapters/mcp/`

核心文件：

```text
adapters/mcp/client.py
```

它做三件事：

```text
1. 读取 mcp_servers.json
2. 创建 MultiServerMCPClient
3. 返回 LangChain 可用的 MCP tools
```

如果配置文件不存在，会返回空工具列表，不影响 Agent 启动。

<a id="adapter-openai"></a>

### `adapters/openai/`

目前是预留目录。

OpenAI-compatible 的基础接入已经在 `adapters/langchain/llm.py` 中完成。

[回到顶部](#top)

---

<a id="runtime"></a>

## 能力层：工具、记忆、数据结构

<a id="tools"></a>

### `tools/`

| 文件 | 状态 | 作用 |
|---|---|---|
| `calculator.py` | 已实现 | 安全计算基础算术表达式 |
| `search.py` | 占位 | 后续可接搜索 |
| `weather.py` | 占位 | 后续可接天气 |

`calculator.py` 使用 `@tool` 包装，所以 LangGraph 的 `ToolNode` 可以直接调用。

<a id="memory"></a>

### `memory/`

| 文件 | 状态 | 作用 |
|---|---|---|
| `short_term.py` | 已实现 | 基于 `InMemorySaver` 的短期记忆 |
| `working_memory.py` | 预留 | 工作记忆 |
| `long_term.py` | 预留 | 长期记忆 |
| `vector_store.py` | 预留 | 向量记忆 |

短期记忆的核心是：

```text
thread_id -> InMemorySaver -> messages state
```

同一个 `thread_id` 共享同一段会话上下文。

<a id="schemas"></a>

### `schemas/`

| 文件 | 数据结构 | 用途 |
|---|---|---|
| `task.py` | `AgentTask` | 用户输入任务 |
| `action.py` | `AgentAction` | 工具动作 |
| `observation.py` | `Observation` | 工具返回观察 |
| `result.py` | `AgentResult` | Agent 最终结果 |
| `plan.py` | `Plan`, `PlanStep` | 后续规划能力 |

这些结构让各层之间传递的数据更清楚。

[回到顶部](#top)

---

<a id="examples-tests"></a>

## 示例和测试

### `examples/`

当前示例：

```text
examples/mcp_math_server.py
```

提供两个 MCP 工具：

```text
add
multiply
```

### `tests/`

| 文件 | 测试内容 |
|---|---|
| `test_calculator.py` | 计算器正常表达式和危险表达式 |
| `test_config.py` | 默认配置 |
| `test_mcp_config.py` | MCP 配置加载 |

运行：

```powershell
python -m pytest -q
```

[回到顶部](#top)

---

<a id="reading"></a>

## 推荐阅读顺序

第一次看项目，推荐这样读：

```text
1. app.py
2. config.py
3. adapters/langgraph/graph.py
4. adapters/langchain/llm.py
5. memory/short_term.py
6. tools/calculator.py
7. adapters/mcp/client.py
8. core/agent.py
9. schemas/
10. interfaces/
```

如果只想理解主流程：

```text
app.py
  -> adapters/langgraph/graph.py
  -> adapters/langchain/llm.py
  -> tools/calculator.py
  -> core/agent.py
```

[回到顶部](#top)

---

<a id="change-map"></a>

## 修改功能时看哪里

| 你想做什么 | 优先看哪里 |
|---|---|
| 新增内置工具 | `tools/calculator.py`, `app.py` |
| 新增 MCP 工具 | `mcp_servers.json`, `adapters/mcp/client.py` |
| 更换 Ollama 模型 | `.env`, `config.py` |
| 接 OpenAI-compatible API | `.env`, `adapters/langchain/llm.py` |
| 改 ReAct 流程 | `adapters/langgraph/graph.py` |
| 增加长期记忆 | `memory/long_term.py`, `interfaces/memory.py` |
| 增加规划能力 | `core/controller.py`, `core/reasoning/`, `schemas/plan.py` |
| 调整返回结构 | `schemas/result.py`, `core/agent.py` |

[回到顶部](#top)

---

<a id="scope"></a>

## 当前项目边界

已实现：

- CLI 启动。
- LangGraph ReAct 图。
- Ollama 模型接入。
- OpenAI-compatible 预留接入。
- 短期记忆。
- 内置 calculator 工具。
- MCP 工具加载。
- MCP 示例 server。
- 基础测试。

暂未实现：

- 长期记忆。
- 向量检索。
- Web UI。
- HTTP API server。
- 真实搜索工具。
- 真实天气工具。
- 完整 Plan&Execute。
- 生产级日志和监控。

[回到顶部](#top)

---

<a id="principles"></a>

## 架构原则

这个项目遵循几个简单原则：

```text
入口只负责组装
核心只负责 Agent 行为
适配器负责接外部框架
工具和记忆独立扩展
数据结构集中定义
接口层稳定边界
```

这样做的好处是：

- 后续换模型更容易。
- 后续换工具来源更容易。
- 后续加长期记忆更容易。
- 后续把 CLI 改成 API 服务也更容易。
- 测试更容易写。

[回到顶部](#top)

---

<a id="diagram"></a>

## 配套架构图

更完整的图在：

```text
Agent架构图.puml
```

可以用 PlantUML 渲染查看。

[回到顶部](#top)
