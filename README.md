# LangChain 1.2 中文学习教程（Codex 版）

> 一份由浅入深、可离线阅读、代码可执行的中文教程。目标是从第一条可预测的工作流开始，逐步掌握记忆、RAG、工具调用和 Agent，最终完成一个具备权限、审批、幂等与审计机制的企业服务台项目。

## 这个教程是为了什么？

学习 LangChain 时，最容易遇到的困难不是记住某一个 API，而是不知道这些概念应该如何组合、为什么组合，以及一个简单的模型调用怎样演进为可以维护和上线的 AI 应用。

本教程希望帮助读者：

- 建立从 Chain、Prompt、Memory、RAG、Tool 到 Agent 的完整知识体系；
- 理解可预测工作流与自主智能体之间的边界，知道什么时候该使用简单方案；
- 掌握 LangChain 1.2 的消息、LCEL、结构化输出、工具、`create_agent`、短期状态与长期 Store 等核心 API；
- 学会处理结构化答案、会话隔离、检索证据、工具权限、运行预算和人工审批；
- 通过五阶段实战项目，理解从 Demo 到企业应用之间缺少哪些工程能力。

教程以真实源码、JSON 正文和可重复执行的验证脚本为依据，而不只是概念介绍。所有页面均能离线阅读，默认示例也不需要 API Key。

## 教程包含哪些内容？

### 第一阶段：基础篇——建立可预测的模型工作流

| 章节 | 内容 | 你会学到什么 |
| --- | --- | --- |
| [01. 环境、版本与第一次运行](./01-setup.html) | 固定依赖、环境验收、首次模型调用 | 建立可复现的 LangChain 1.2 开发环境 |
| [02. 模型与消息](./02-messages.html) | 模型、消息角色、一次调用的生命周期 | 理解输入消息、模型响应和消息历史 |
| [03. 提示模板](./03-prompts.html) | 模板变量、消息占位符、提示设计 | 把自然语言输入变成稳定、可测试的契约 |
| [04. Chain 与 LCEL](./04-chains.html) | `Runnable`、管道、同步/异步、组合与错误处理 | 用 LCEL 编排清晰、可组合的工作流 |
| [05. 结构化输出](./05-structured.html) | Pydantic Schema、类型化结果 | 让模型答案能够可靠地进入后续程序 |
| [06. 工具调用](./06-tools.html) | 定义工具、参数 Schema、绑定与执行 | 让模型以结构化方式请求外部能力 |
| [07. Agent](./07-agents.html) | Agent 循环、工具调用轨迹、`create_agent` | 理解智能体如何决策并形成调用循环 |

### 第二阶段：检索与记忆——让应用拥有上下文

| 章节 | 内容 | 你会学到什么 |
| --- | --- | --- |
| [08. Memory](./08-memory.html) | 短期状态、长期 Store、会话隔离 | 在连续对话与数据边界之间取得平衡 |
| [09. RAG 索引](./09-rag-index.html) | 文档切分、元数据、向量与索引 | 把原始文档转换为可检索的证据 |
| [10. RAG 回答](./10-rag-answer.html) | 检索、引用验证、无证据拒答 | 让回答能够追溯来源并保持诚实 |
| [11. Agentic RAG](./11-agentic-rag.html) | 检索工具、运行时身份、权限边界 | 把“是否检索”与“允许访问什么”分开治理 |

### 第三阶段：工程化——让系统可测试、可观察、可部署

| 章节 | 内容 | 你会学到什么 |
| --- | --- | --- |
| [12. 中间件、流式输出与运行预算](./12-runtime.html) | 中间件、流式事件、错误处理、并发与预算 | 为 Agent 增加横切能力和运行约束 |
| [13. 测试、评估与可观察性](./13-testing.html) | 组件测试、轨迹断言、任务评估 | 建立可重复的质量验证方式 |
| [14. 安全、性能与部署边界](./14-production.html) | 身份认证、租户隔离、性能、部署检查 | 识别上线前必须补齐的生产化能力 |

### 第四阶段：递进实战——从单工具到企业服务台

实战部分使用同一个“企业服务台”场景，每个阶段只增加一组新能力，便于观察架构如何自然演进：

1. [实战 1：单工具企业服务台](./15-project-1.html)——完成基本工具调用；
2. [实战 2：多工具与任务边界](./16-project-2.html)——组合多个工具并限制职责；
3. [实战 3：会话记忆与隔离](./17-project-3.html)——加入短期状态并隔离不同会话；
4. [实战 4：企业知识与权限 RAG](./18-project-4.html)——引入检索、引用和租户权限；
5. [实战 5：审批、幂等与审计](./19-project-5.html)——加入 Human-in-the-loop、幂等写入和审计记录。

### 第五阶段：迁移与参考

| 章节 | 内容 |
| --- | --- |
| [20. 迁移与排错](./20-migration.html) | 新旧 API 对照、版本差异、导入与运行问题 |
| [21. 参考手册](./21-reference.html) | 术语表、逐页目录、代码速查与完整索引 |

## 教程特点

- **22 个互相链接的静态页面**：无需服务器、构建步骤或联网即可阅读；
- **14 组独立章节示例**：使用真实 LangChain 执行对象，并通过回归脚本验证；
- **五阶段递进项目**：每阶段都有明确目标、边界和可执行入口；
- **正文与代码单一来源**：`content/*.json` 与 `examples/`、`project/` 是真源，HTML 由构建器生成，避免内容漂移；
- **离线优先**：本地 CSS、JavaScript 和语法高亮资源，不依赖 CDN；
- **学习进度可迁移**：完成状态保存在浏览器本地，并支持 JSON 导入/导出；
- **工程质量可复核**：包含静态检查、代码回归、浏览器离线验收和打包工具。

## 快速开始

### 只阅读教程

直接用浏览器打开 [`index.html`](./index.html)，从学习路线首页开始。

### 运行章节示例

基线环境为 Python 3.12 与 LangChain 1.2.0。完整依赖已记录在 `requirements.lock.txt` 中：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe examples/01_check_environment.py
.\.venv\Scripts\python.exe tools/run_examples.py
```

macOS/Linux 可激活 `.venv/bin/activate` 后使用 `python`。

默认示例使用明确标注的确定性模型替身，不需要 API Key，也不会发起真实模型请求。部分脚本和实战入口支持 `--live`，会读取 `OPENAI_API_KEY` 与 `OPENAI_MODEL`；在线模式需要网络、可用模型和有效凭据。

### 运行五阶段实战

```powershell
.\.venv\Scripts\python.exe project\stage1.py
.\.venv\Scripts\python.exe project\stage2.py
.\.venv\Scripts\python.exe project\stage3.py
.\.venv\Scripts\python.exe project\stage4.py
.\.venv\Scripts\python.exe project\stage5.py
```

第五阶段默认只展示待审批动作。离线演示可使用 `--decision approve` 或 `--decision reject`；在线模式在展示实际动作后还会要求终端确认。项目回归可运行：

```powershell
.\.venv\Scripts\python.exe project\check_project.py
```

## 重新构建与验证

```powershell
.\.venv\Scripts\python.exe tools/build_site.py
.\.venv\Scripts\python.exe tools/check_site.py
.\.venv\Scripts\python.exe tools/run_examples.py
.\.venv\Scripts\python.exe tools/browser_check.py
```

- `build_site.py`：从 JSON 正文与真实源码重新生成 HTML；
- `check_site.py`：检查本地链接、锚点、资源、结构和 Python 语法；
- `run_examples.py`：运行 14 组章节示例及项目回归；
- `browser_check.py`：在桌面与手机视口进行断网浏览器验收；
- `package_site.py`：按白名单打包，排除虚拟环境、临时数据和密钥文件。

验证报告与截图位于 [`validation/`](./validation)。

## 目录结构

```text
langchain-1.2-tutorial/
├── index.html + 01-setup.html … 21-reference.html  # 生成后的教程页面
├── assets/                 # 本地样式、脚本、高亮和课程目录
├── content/                # 22 份教程正文 JSON（内容真源）
├── examples/               # 14 组独立示例及共用辅助代码
├── project/                # 五阶段企业服务台及回归检查
├── tools/                  # 构建、检查、回归、浏览器验证和打包工具
├── validation/             # 验证报告与页面截图
├── requirements.txt        # 直接依赖
├── requirements.lock.txt   # 完整依赖快照
├── README.md
└── HANDOFF.md              # 项目交接、关键决策和验证记录
```

`.venv/`、`.tmp/`、本地环境变量文件、临时数据库和本地审计日志均已通过 `.gitignore` 排除。

## 适合谁？

- 希望系统学习 LangChain 1.2，而不是只跟随零散示例的开发者；
- 已经会调用模型 API，并想进一步学习工作流、RAG、Agent 与生产化的开发者；
- 需要参考企业 Agent、权限隔离、人工审批和测试实践的团队成员；
- 正在从旧版 LangChain 迁移，并希望理解新旧 API 边界的开发者。

## 版本与验证边界

教程以 Python `langchain==1.2.0` 为基准，完整锁定版本见 `requirements.lock.txt`。当前交付已完成离线代码回归、静态站点检查、桌面与手机浏览器离线验收；真实模型 API 响应质量、真实语义向量效果和生产负载不在本次验证范围内。

更多维护状态、限制和复现记录见 [`HANDOFF.md`](./HANDOFF.md)。
