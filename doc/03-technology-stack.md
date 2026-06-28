# ScholarPilot Technology Stack

---

## 1. 技术选型结论

ScholarPilot 优先建设为 **浏览器访问的 Web Research Workspace**，采用前后端分离架构：

```text
Next.js Web UI
  -> FastAPI Backend
  -> PostgreSQL / Qdrant / Redis
  -> RAG Pipeline / Agent Workflow
  -> LLM / Embedding / Reranker Providers
```

第一版标准技术栈：

```text
Frontend:
Next.js + React + TypeScript + Tailwind CSS + shadcn/ui + TanStack Query + PDF.js

Backend:
Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2.0 + Alembic + uv + Ruff + Pytest

Storage:
PostgreSQL + Qdrant + Redis + local filesystem

Async:
RQ + Redis

RAG:
Custom RAG Pipeline + Qdrant Hybrid Search + BM25 + Reranker

Agent:
LangGraph

Parsing:
PyMuPDF + pdfplumber first
GROBID / Docling later

Models:
Provider abstraction
Qwen / DeepSeek / OpenAI
BGE-M3 / Qwen3 Embedding
BGE Reranker / Qwen3 Reranker

Ops:
Docker Compose later
Langfuse / Phoenix later
```

核心判断：

- 先做 Web 服务，不先做桌面软件。
- 先做稳定 RAG 闭环，不先做复杂 Agent。
- 先做轻量可控技术栈，不一开始引入重型分布式组件。
- 模型、向量库、解析器必须通过接口隔离，方便后续替换。

---

## 2. 产品形态选择

### 2.1 推荐形态

推荐做成：

```text
浏览器 Web App + 后端服务
```

也就是：

- 用户通过浏览器访问 ScholarPilot。
- 前端负责文档库、阅读器、Chat、引用面板、任务状态。
- 后端负责文档解析、检索、embedding、LLM 调用、Agent 工作流。
- 数据库、向量库、缓存和文件存储由后端统一管理。

### 2.2 不优先做桌面软件

桌面软件会过早引入以下复杂度：

- 安装包构建。
- 自动更新。
- 跨平台兼容。
- 本地 Python 环境管理。
- 本地数据库和向量库管理。
- 模型依赖和 GPU 环境差异。

这些问题会拖慢 Phase 0 和 Phase 1。当前阶段最重要的是跑通：

```text
上传 PDF -> 解析 -> chunk -> embedding -> 检索 -> 问答 -> 引用返回
```

### 2.3 后续桌面封装

如果后续需要桌面形态，可以采用：

```text
Electron / Tauri
  -> 内嵌 Web UI
  -> 调用本地 FastAPI 服务
```

桌面客户端只作为外壳，不改变核心架构。

---

## 3. 前端技术栈

### 3.1 推荐方案

```text
Next.js + React + TypeScript + Tailwind CSS + shadcn/ui + TanStack Query + PDF.js
```

### 3.2 选型理由

| 技术 | 用途 | 理由 |
|---|---|---|
| Next.js | Web 应用框架 | 适合复杂 Web App，生态成熟，后续部署方便 |
| React | UI 基础 | 适合 Chat、PDF 阅读器、引用面板等复杂交互 |
| TypeScript | 类型约束 | 降低前后端接口变更风险 |
| Tailwind CSS | 样式系统 | 快速构建统一、可维护的界面 |
| shadcn/ui | UI 组件 | 适合构建专业工作台界面，可控性强 |
| TanStack Query | 服务端状态 | 适合文档列表、任务状态、检索结果和 Chat 历史 |
| PDF.js / react-pdf | PDF 阅读 | 支持页码定位、引用跳转和论文阅读器 |

### 3.3 前端不推荐项

| 技术 | 暂不推荐原因 |
|---|---|
| 纯 Vite SPA | 可以用，但后续路由、部署、服务边界不如 Next.js 统一 |
| Electron | 当前阶段会增加桌面端构建和环境管理成本 |
| 复杂动画库 | 当前重点是阅读、检索和引用，不是视觉动效 |
| 大型状态管理库 | 早期 Zustand/TanStack Query 足够，不需要 Redux 级复杂度 |

### 3.4 前端结构建议

```text
frontend/
├─ app/
├─ components/
│  ├─ document/
│  ├─ chat/
│  ├─ citation/
│  └─ layout/
├─ lib/
│  ├─ api-client.ts
│  ├─ query-client.ts
│  └─ types.ts
└─ package.json
```

---

## 4. 后端技术栈

### 4.1 推荐方案

```text
Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2.0 + Alembic + uv + Ruff + Pytest
```

### 4.2 选型理由

| 技术 | 用途 | 理由 |
|---|---|---|
| Python 3.12 | 后端语言 | AI、RAG、PDF 解析生态最完整 |
| FastAPI | API 服务 | 类型友好，异步支持好，适合 AI 服务接口 |
| Pydantic v2 | 数据校验 | 请求、响应和配置结构清晰 |
| SQLAlchemy 2.0 | ORM | 适合 PostgreSQL 数据访问和复杂查询 |
| Alembic | 数据库迁移 | 保证模型变化可追踪 |
| uv | Python 依赖管理 | 快速、现代、适合锁定依赖 |
| Ruff | lint / format | 速度快，统一代码风格 |
| Pytest | 测试 | Python 主流测试工具 |

### 4.3 后端结构建议

```text
backend/
├─ app/
│  ├─ api/
│  ├─ core/
│  ├─ models/
│  ├─ schemas/
│  ├─ services/
│  ├─ repositories/
│  ├─ providers/
│  └─ main.py
├─ tests/
├─ pyproject.toml
└─ uv.lock
```

### 4.4 分层职责

| 层 | 职责 |
|---|---|
| api | HTTP 路由、请求参数、响应格式 |
| schemas | Pydantic DTO、输入输出结构 |
| services | 业务流程编排 |
| repositories | 数据访问 |
| models | 数据库模型 |
| providers | 外部模型、向量库、解析器、论文搜索服务适配 |
| core | 配置、日志、异常、基础设施 |

### 4.5 后端不推荐项

| 技术或做法 | 暂不推荐原因 |
|---|---|
| Django | 管理后台强，但当前 AI/RAG 服务更适合 FastAPI |
| Flask | 简洁，但类型、异步和 schema 体系不如 FastAPI 直接 |
| API 层写业务逻辑 | 会导致耦合严重，后续难测试 |
| 业务代码直接调用模型厂商 SDK | 会锁死 provider，不利于切换模型 |

---

## 5. 数据库、向量库与缓存

### 5.1 推荐方案

```text
PostgreSQL + Qdrant + Redis + local filesystem
```

### 5.2 PostgreSQL

用于存储：

- project
- document
- chunk metadata
- citation
- task
- evaluation run
- user feedback

不建议把所有结构化数据塞进向量库。向量库负责相似度检索，PostgreSQL 负责业务元数据和事务一致性。

### 5.3 Qdrant

推荐 Qdrant 作为第一版服务化向量库。

理由：

- 部署轻。
- API 友好。
- 支持 payload metadata。
- 适合从 MVP 过渡到中等规模服务。
- 适合 dense / sparse / hybrid 检索路线。

### 5.4 FAISS

FAISS 适合：

- 本地实验。
- 快速验证 embedding 效果。
- 单机小规模索引。

但不建议作为 Web 服务主向量库，因为服务化管理、metadata 过滤、持久化和运维便利性不如 Qdrant。

### 5.5 Milvus

Milvus 适合：

- 大规模向量数据。
- 更重的服务化部署。
- 多节点扩展。

当前阶段不优先引入。等数据规模和并发需求明显上来后再评估。

### 5.6 Redis

用于：

- 异步任务队列。
- 任务状态缓存。
- query rewrite 缓存。
- embedding 缓存。
- 检索结果短期缓存。
- API 限流。

---

## 6. 异步任务

### 6.1 推荐方案

```text
Phase 1: RQ + Redis
Phase 2-3: RQ 或 Celery
Phase 4+: 如长工作流复杂，再评估 Temporal
```

### 6.2 选型理由

| 技术 | 适用场景 | 当前判断 |
|---|---|---|
| RQ | 简单后台任务 | Phase 1 推荐 |
| Celery | 更复杂的分布式任务 | Phase 2/3 再评估 |
| Dramatiq | 中等复杂度任务 | 可作为 Celery 替代 |
| Temporal | 长生命周期可靠工作流 | 后期再看 |

### 6.3 任务类型

异步任务包括：

- PDF 解析。
- chunk 切分。
- embedding 生成。
- 向量索引。
- 批量论文导入。
- 多论文对比。
- related work 生成。
- 趋势报告生成。

---

## 7. RAG 技术栈

### 7.1 推荐方案

```text
Custom RAG Pipeline + Qdrant Hybrid Search + BM25 + Reranker
```

### 7.2 为什么自研核心 Pipeline

ScholarPilot 的核心竞争力是：

- Evidence Pack。
- citation grounding。
- 检索 trace。
- 引用准确性检查。
- RAG 评测闭环。

这些能力需要较强控制力。如果一开始完全依赖重型框架，核心链路容易被框架抽象遮住，不利于调试和评测。

### 7.3 推荐 RAG 流程

```text
question
  -> query classification
  -> query rewrite / decomposition
  -> dense retrieval
  -> sparse retrieval
  -> RRF fusion
  -> rerank
  -> evidence pack
  -> answer generation
  -> citation verification
  -> answer with sources
```

### 7.4 可参考框架

| 框架 | 用途 | 当前策略 |
|---|---|---|
| LangChain | 工具生态丰富 | 不作为核心依赖，按需参考 |
| LlamaIndex | 数据接入和索引生态强 | 可参考，不锁死 |
| Haystack | RAG pipeline 成熟 | 可参考 pipeline 思路 |
| RAGAS | RAG 评测 | 推荐接入或参考指标 |

---

## 8. Agent 技术栈

### 8.1 推荐方案

```text
LangGraph
```

### 8.2 选型理由

LangGraph 适合状态机式、可控 Agent 工作流。ScholarPilot 需要的是科研任务编排，不是自由聊天机器人。

适合 LangGraph 的任务：

- 单篇论文总结。
- 多论文对比。
- Related Work 草稿。
- 趋势报告。
- 多步检索。
- 人工确认节点。
- 失败恢复。

### 8.3 Agent 设计边界

```text
Planner Agent
  -> Retriever Agent
  -> Evidence Synthesizer
  -> Reviewer Agent
```

每个 Agent 必须：

- 输入明确。
- 输出明确。
- 工具权限明确。
- 最大迭代次数明确。
- trace 可记录。

---

## 9. 文档解析技术栈

### 9.1 推荐路线

```text
Phase 1:
PyMuPDF + pdfplumber

Phase 2:
GROBID

Phase 3/4:
Docling
```

### 9.2 工具职责

| 工具 | 职责 |
|---|---|
| PyMuPDF | 快速提取 PDF 文本、页码、基础结构 |
| pdfplumber | 表格和局部版面辅助解析 |
| GROBID | 学术论文标题、作者、摘要、参考文献等结构化元数据 |
| Docling | 复杂版面、表格、公式、图注、多格式文档解析 |
| BeautifulSoup / trafilatura | Web 页面正文抽取 |

### 9.3 不一开始强依赖 Docling 的原因

Docling 能力更强，但第一阶段目标是稳定跑通 RAG 闭环。过早把复杂解析作为硬依赖，会增加调试范围。

第一阶段只要求：

- 常规论文 PDF 可解析。
- 页码能保留。
- chunk 能回到来源。
- 文本质量足以支持问答。

---

## 10. 模型技术栈

### 10.1 核心原则

模型必须通过 provider abstraction 接入。业务代码不能直接绑定某个厂商或某个模型。

建议抽象：

```text
LLMProvider
EmbeddingProvider
RerankerProvider
```

### 10.2 LLM

推荐支持：

- Qwen
- DeepSeek
- OpenAI
- Llama / local model

策略：

- 默认选一个稳定 LLM 跑通 MVP。
- 复杂任务使用能力更强的模型。
- 简单任务使用成本更低的模型。
- 模型切换不影响业务层代码。

### 10.3 Embedding

推荐：

- BGE-M3
- Qwen3 Embedding
- E5
- OpenAI text embeddings 作为云端备选

选择依据：

- 中英文混合能力。
- 学术文本表现。
- 向量维度和成本。
- 本地部署便利性。

### 10.4 Reranker

推荐：

- BGE Reranker
- Qwen3 Reranker

Reranker 放在二阶段排序中，用于提升最终 Evidence Pack 质量。

---

## 11. 评测与可观测

### 11.1 RAG 评测

推荐：

```text
RAGAS + 自建固定问题集
```

关键指标：

- Recall@K
- MRR
- Context Precision
- Context Recall
- Faithfulness
- Answer Relevance
- Citation Accuracy

### 11.2 Trace

Phase 1 先自建 JSON trace：

```json
{
  "query": "...",
  "rewritten_query": "...",
  "dense_results": [],
  "sparse_results": [],
  "reranked_results": [],
  "evidence_pack": [],
  "model": "...",
  "latency_ms": 1234
}
```

Phase 3 后再评估：

- Langfuse
- Phoenix
- OpenTelemetry

### 11.3 错误监控

Phase 5 可考虑：

- Sentry
- OpenTelemetry
- 结构化日志平台

---

## 12. 安全技术要求

### 12.1 文档不可信原则

以下内容全部视为不可信输入：

- 上传 PDF。
- 网页正文。
- README。
- 外部论文摘要。
- 用户粘贴内容。

### 12.2 Prompt Injection 防护

必须做到：

- 检索内容只能作为 evidence，不允许覆盖系统指令。
- 文档中的命令式文本不能直接触发工具调用。
- Agent 工具权限由后端策略控制。
- 高风险动作需要人工确认。

### 12.3 密钥管理

- 密钥只能放在环境变量。
- `.env` 不提交 Git。
- 提供 `.env.example`。
- 日志不能打印 API key、token、cookie。

---

## 13. 分阶段采用策略

### Phase 0：项目基础

采用：

- Next.js
- FastAPI
- Python 3.12
- uv
- Ruff
- Pytest
- TypeScript
- Tailwind CSS

暂不引入：

- LangGraph
- Qdrant
- Redis
- Reranker

### Phase 1：单篇论文 RAG MVP

采用：

- PostgreSQL
- Qdrant
- Redis
- RQ
- PyMuPDF
- pdfplumber
- embedding provider
- LLM provider

暂不引入：

- GraphRAG
- 复杂 Agent
- Docling 作为硬依赖
- Milvus

### Phase 2：高质量 Hybrid RAG

采用：

- BM25
- dense retrieval
- RRF
- reranker
- Evidence Pack
- RAGAS 或自建评测集

### Phase 3：科研任务工作流

采用：

- LangGraph
- Agent trace
- 长任务状态管理
- 多论文任务编排

### Phase 4：趋势追踪与知识增强

采用：

- arXiv / Semantic Scholar / OpenAlex
- GROBID
- Docling
- GraphRAG 原型
- 聚类分析

### Phase 5：产品化部署

采用：

- Docker Compose
- 对象存储
- 日志与监控
- 限流
- 备份策略
- 错误追踪

---

## 14. 技术变更规则

### 14.1 允许变更

如果需要替换技术栈，必须满足：

- 有明确原因。
- 有替代方案分析。
- 不破坏既有阶段目标。
- 不引入明显过重复杂度。
- 更新本文档和 `RULE.md` 中相关约束。

### 14.2 禁止随意引入

以下内容不得随意引入：

- 新数据库。
- 新向量库。
- 新 Agent 框架。
- 新前端 UI 框架。
- 新模型供应商 SDK。
- 新任务队列。

引入前必须说明：

- 解决什么问题。
- 为什么现有技术不能解决。
- 对部署、测试和维护的影响。

---

## 15. 当前最终建议

ScholarPilot 第一阶段不需要追求“技术最满”，而要追求“链路最稳”：

```text
Next.js UI
  -> FastAPI API
  -> PostgreSQL metadata
  -> Qdrant vectors
  -> Redis/RQ async jobs
  -> PyMuPDF/pdfplumber parsing
  -> embedding
  -> retrieval
  -> LLM answer
  -> citation output
```

这条链路稳定以后，再逐步加入：

- Hybrid Retrieval
- Reranker
- RAGAS
- LangGraph
- Docling
- GraphRAG
- Docker Compose

最终原则：

> 技术栈服务于 ScholarPilot 的核心目标：可信、可追溯、可评测的科研知识工作台。
