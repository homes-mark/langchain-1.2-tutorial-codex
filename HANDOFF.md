# LangChain 1.2 中文教程交接

更新时间：2026-10-26（Asia/Shanghai）。工作根目录：`D:\langchain-works\langchain-1.2-tutorial`。

## 1. 任务与验收目标

用户要求一套完整、由浅入深的中文 LangChain 1.2 教程，多个互相链接的 HTML 文件；各页有学习路径、目标、前置、难度、真实代码、三级练习及验证、误区与最佳实践；企业 Agent 五阶段增量实战；页内目录、高亮、进度与完全离线阅读；额外交接文件，下一会话仅读此文件即可接手。用户最后要求目录规划、各页内容要点与交接组织方式；已选择实际交付完整站点，同时在首页和21提供规划与索引。

## 2. 已完成

- 22份正文 JSON、22个生成 HTML，所有页面共用本地CSS/JS/构建期高亮，无远程资源依赖。
- 01–14的14个独立示例及共用模型/向量检索辅助代码。
- 企业服务台单工具→多工具→记忆→带权限的知识检索→HITL审批/幂等/审计五阶段项目。
- 默认所有代码不需API密钥；部分脚本与项目支持 `--live`，真实模型分支明确未验证。
- 精确依赖已安装于 `.venv` 并锁定。历史传递依赖导入问题已修复。
- 构建、静态检查、示例回归、浏览器离线验证与交付打包工具均已实现。
- README包含使用方法；21-reference包含逐页目录与内容摘要。
- RAG章节10/11已补齐 `--live --question` 入口；在线分支不再套用固定文本或固定工具调用ID断言，保留引用与授权检查。
- 最终代码回归15/15、静态站点检查及22页双视口浏览器检查全部通过，详见第6节。

## 3. 当前状态与停止位置

内容制作、代码验证、页面构建及浏览器验收均已完成，无未完成的教程事项。交付压缩包由 `tools/package_site.py` 生成到根目录旁的 `D:\langchain-works\langchain-1.2-tutorial.zip`；重新运行该脚本可重建。在线真实模型调用属于明确未验证范围，不影响已交付的离线教程。下一会话可以直接处理用户提出的增补，不需要重做本次基础工作。

## 4. 关键决策与版本

- 解释用户的 LangChain 1.2 为 Python `langchain==1.2.0`，不是JS，也不声称是当前最新版。
- 验证环境：Windows、Python 3.12.10。核心固定：core1.2.5、langgraph1.0.5、prebuilt1.0.5、openai适配1.1.6、splitters1.1.0、numpy2.2.6、pygments2.19.2。完整传递版本见 requirements.lock.txt。
- 当前官网文档会更新到新版本；必须以1.2.0固定源码和本地执行证据为准。没有采用1.3的 stream_events(version="v3")、新版runtime.execution_info/server_info或新版HITL参数。
- Chain 用 LCEL/Runnable；Agent 用 `create_agent`；短期Memory用checkpointer+thread_id，长期用Store namespace。旧LLMChain/ConversationBufferMemory仅作迁移对照。
- 离线模型 `examples/common.py:ScriptedChatModel` 按预定响应顺序输出，支持bind_tools，只验证框架协议，不推理且不并发安全。每个独立运行创建新实例。
- RAG向量器是显式关键词特征，未假装为语义embedding；真正语义检索、模型质量与生产认证需要后续集成。
- 实战固定可信身份模拟认证后的上下文；租户与用户权限在工具执行层检查。namespace本身不是授权。
- 受控写入用1.2支持的HumanInTheLoopMiddleware和Command恢复；数据库采用SQLite唯一请求键与事务。它是企业机制教学实现，不是可直接上线的完整企业服务。
- 静态站点支持file://；进度存localStorage并随站内HTML链接携带，允许导出/导入。没有fetch、服务端、CDN或远程字体。

## 5. 目录与页面地图

```text
index.html                         学习路径、概念关系、使用方式
01-setup.html                      固定依赖、环境验收、可选真实模型
02-messages.html                   模型与消息角色
03-prompts.html                    提示模板、变量、历史占位
04-chains.html                     LCEL、invoke/batch/ainvoke、组合
05-structured.html                 Pydantic与结构化输出
06-tools.html                      定义/绑定/执行/回传
07-agents.html                     Agent循环与步骤流
08-memory.html                     短期状态、长期Store、隔离
09-rag-index.html                  切分、元数据、向量与索引
10-rag-answer.html                 检索、引用验证、无证据拒答
11-agentic-rag.html                 检索工具与运行时身份
12-runtime.html                    中间件、错误、预算、并发
13-testing.html                    组件/轨迹/集成/任务评估
14-production.html                 权限、安全、性能与部署缺口
15-project-1.html … 19-project-5.html 五阶段企业服务台
20-migration.html                  旧版迁移、版本与导入排错
21-reference.html                  术语、逐页概览、目录与交接规范
content/*.json                     以上页面的正文真源
assets/site.css,site.js,syntax.css  本地样式、进度交互、高亮
assets/catalog.json                构建生成目录；浏览器不fetch
examples/01_*.py … 14_*.py          章节可运行完整示例
examples/common.py,rag_support.py  确定性模型和关键词向量支持
project/helpdesk.py                共用项目实现
project/stage1.py … stage5.py       各阶段短入口
project/check_project.py           业务与安全边界回归
tools/build_site.py                JSON+真实源码→HTML
tools/check_site.py                本地链接/锚点/离线资源/结构/语法
tools/run_examples.py              14章+项目回归，输出report.json
tools/browser_check.py             Chrome/Edge无界面离线与交互验证
tools/package_site.py              明确白名单文件打包，排除环境/临时数据
validation/report.json             15项离线回归实际输出
validation/site-report.json        22页结构、链接、资源与Python语法检查
validation/browser-report.json     离线双视口与进度交互结果
validation/*.png                   桌面首页、实战页、手机首页截图
requirements.txt,requirements.lock.txt
README.md,HANDOFF.md
.venv/,.tmp/                       本机环境与临时目录，不进交付包
```

## 6. 重现命令与验证事实

所有命令在教程根目录运行；Windows无需激活可直接使用解释器：

```powershell
.\.venv\Scripts\python.exe -X utf8 tools/build_site.py
.\.venv\Scripts\python.exe -X utf8 tools/check_site.py
.\.venv\Scripts\python.exe -X utf8 tools/run_examples.py
.\.venv\Scripts\python.exe -X utf8 tools/browser_check.py
.\.venv\Scripts\python.exe -X utf8 tools/package_site.py
python -m pip --python .\.venv\Scripts\python.exe check
```

首次重建环境：`python -m venv .venv` 然后 `.venv\Scripts\python.exe -m pip install -r requirements.lock.txt`。

最终验证事实：

| 验证 | 实际结果 | 证据 |
|---|---|---|
| 离线代码全量回归 | 15/15通过，含14章独立示例和项目回归 | validation/report.json |
| 项目行为 | 五阶段、会话隔离、ACL、HITL pending/reject/approve、幂等和审计通过 | 同上项目输出及project/check_project.py断言 |
| 静态站点 | 22 HTML + 22 JSON；1,269本地引用；28 Python语法解析；零失败 | validation/site-report.json |
| 浏览器 | Windows Chrome；file://+断网模拟；22页在1440×1000和390×844均无整页横向溢出 | validation/browser-report.json |
| 交互 | 站内跳转、标记/刷新、章节筛选、进度文件导入/导出、手机菜单、本地存储被禁用时的进度传递均通过 | browser-report.json |
| 离线资源 | 浏览器未发起页面远程资源请求，未捕获JS异常 | browser-report.json |
| 依赖 | pip check无损坏依赖，真实导入与Agent invoke通过 | 环境脚本及本会话实际输出 |

已查看三张浏览器截图，中文排版、侧栏、学习目标区和移动端布局正常。最后一次全量运行在10/11加入在线入口后完成，依然15/15。首次沙箱内的04超时已由自动批准的提升执行解决，最终报告没有遗留失败。浏览器检查仅覆盖Chrome，不声称所有浏览器均已验证。

## 7. 限制与排错

- 未请求任何真实模型API；没有测在线质量、费用、真实语义向量或生产容量。
- `.venv`建立时沙箱系统TEMP写入失败；可把TEMP/TMP设到工作根的 `.tmp` 再安装。普通用户环境通常无需此措施。runner已设置本地临时目录。
- Windows受限沙箱会阻止asyncio创建本地socket，表现为04超时，非框架API失败。工具允许时在提升环境执行验证；不要为规避环境问题删掉异步教学内容。
- 安装器曾解析prebuilt1.0.10，它与graph1.0.5导入不兼容，pip check仍通过；已降到prebuilt1.0.5并固定。
- InMemoryVectorStore需要可选NumPy，已纳入锁文件。
- 参考外链需要联网；网页正文、高亮、导航与默认示例（依赖预装后）可离线。未打包wheelhouse、模型权重或虚拟环境。
- 浏览器file://存储行为不统一，进度导出是跨浏览器/目录迁移的可靠备份。浏览器测试结果必须写明浏览器与视口。

## 8. 下一步与维护规则

1. 当前没有必须继续的未完成事项；按用户后续需求选择深化章节或接入实际模型。
2. 每次后续修改更新此文件的状态、验证数字与限制，保证下次只读此文件即可了解实际完成情况。
3. 打包时排除 `.venv`、`.tmp`、`__pycache__`、临时数据库与任何密钥；保留完整页面相对结构。
4. 以后修改正文改content JSON，修改示例改真实Python源，再运行build_site/check_site。不要只改生成HTML。
5. 若用户要在线扩展，先确认可用提供商/模型与数据边界，实际运行指定分支后再更新“已验证”声明。若要生产化，从14列出的认证与持久化缺口开始。

无需等待任何子代理：所有内容与工具交付已合并在共享工作目录。本任务未建立Git仓库，未提交或发布到外部服务。
