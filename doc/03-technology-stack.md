# Kairos Technology Stack

---

## 1. 技术栈结论

Kairos 新定位为可验证的团队知识库问答与知识运营平台，但现有技术栈仍然适用。当前不需要推翻重来，应在现有 Web 架构和 RAG 引擎上扩展知识库、反馈、知识运营、权限、trace、评测和后期 Agent 能力。

标准架构：

```text
Next.js Web UI
  -> FastAPI Backend
  -> PostgreSQL / Qdrant / Redis
  -> Document Pipeline / Hybrid RAG / Feedback / Trace
  -> Knowledge Operations
  -> Controlled Multi-Agent Workflow (later)
  -> LLM / Embedding / Reranker Providers
```

核心判断：

- 继续优先 Web App，不做桌面客户端。
- 继续保留 FastAPI + Next.js + PostgreSQL + Qdrant + Redis。
- 继续自研核心 RAG pipeline，避免核心链路被重型框架遮蔽。
- 产品落点优先是知识库问答、用户反馈和知识运营闭环。
- Agent 后置到知识库、权限、反馈和 trace 基础稳定之后。
- 后续工具采用分层策略：短期不堆工具，中期补评测和观测，长期按瓶颈升级检索、解析和权限系统。

---

## 2. 前端技术栈

| 技术 | 用途 | 当前策略 |
|---|---|---|
| Next.js | Web 应用框架 | 保留 |
| React | 复杂交互 UI | 保留 |
| TypeScript | 前后端契约和类型安全 | 保留 |
| Tailwind CSS | 工作台样式系统 | 保留 |
| TanStack Query | 服务端状态、轮询、缓存 | 已使用，继续扩大 |
| shadcn/ui | 标准组件库 | 可逐步引入，不强制一次迁移 |
| PDF.js / react-pdf | PDF 阅读器和引用跳转 | Phase 3/4 引入 |
| ECharts / Recharts | 统计看板 | Phase 6 再引入 |

前端结构建议：

```text
frontend/
├─ app/
├─ components/
│  ├─ knowledge-base/
│  ├─ document/
│  ├─ chat/
│  ├─ citation/
│  ├─ feedback/
│  ├─ trace/
│  └─ dashboard/
├─ lib/
│  ├─ api-client.ts
│  └─ types.ts
└─ package.json
```

当前前端已有三栏工作区。下一阶段应增加知识库切换和知识库文档分组，而不是重做 UI。

---

## 3. 后端技术栈

| 技术 | 用途 | 当前策略 |
|---|---|---|
| Python 3.12 | AI/RAG 后端语言 | 保留 |
| FastAPI | API 服务 | 保留 |
| Pydantic v2 | 请求、响应、配置 schema | 保留 |
| SQLAlchemy 2.0 | PostgreSQL ORM | 保留 |
| Alembic | 数据库迁移 | 保留 |
| uv | Python 依赖管理 | 保留 |
| Ruff | lint/format | 保留 |
| Pytest | 测试 | 保留 |

后端结构继续采用：

```text
backend/app/
├─ api/
├─ core/
├─ models/
├─ schemas/
├─ services/
├─ repositories/
├─ providers/
└─ workers/
```

新增模块建议：

```text
models/knowledge_base.py
repositories/knowledge_base_repo.py
api/knowledge_bases.py
services/trace_service.py
services/feedback_service.py
services/knowledge_ops_service.py
services/eval_service.py
services/agent_service.py
```

---

## 4. 存储与基础设施

| 组件 | 用途 | 当前策略 |
|---|---|---|
| PostgreSQL | 用户、知识库、文档、chunk、trace、评测、审计 | 主业务数据库 |
| Qdrant | 向量索引和 metadata filter | 继续使用 |
| Redis | RQ 队列、任务状态、缓存 | 继续使用 |
| Local filesystem | 原始文档保存 | 当前保留 |
| MinIO / S3 | 对象存储 | 生产化阶段再评估 |

PostgreSQL 数据模型应逐步补齐：

- `knowledge_bases`
- `users`
- `roles`
- `audit_logs`
- `chat_sessions`
- `chat_messages`
- `feedback_events`
- `knowledge_gaps`
- `knowledge_ops_items`
- `retrieval_traces`
- `eval_datasets`
- `eval_runs`

第一步只新增知识库相关表，避免一次性迁移过大。

### 4.1 暂不替换的组件

| 组件 | 暂不替换原因 | 后续替代候选 |
|---|---|---|
| PostgreSQL | 当前业务数据规模和事务需求适配良好 | 不建议替换 |
| Qdrant | 已接入，适合当前向量检索和 metadata filter | Milvus、Elasticsearch/OpenSearch |
| Redis/RQ | 已满足文档处理异步任务 | Celery、Dramatiq、Temporal |
| Local filesystem | 开发期简单可靠 | MinIO、S3 |

只有出现明确瓶颈时才升级，不能因为工具流行而替换。

---

## 5. 异步任务

当前使用 RQ + Redis，适合现阶段：

- 文档解析。
- chunk 切分。
- embedding 生成。
- 向量索引。
- 文档重新索引。

暂不切换 Celery。只有当出现复杂定时任务、任务编排、失败恢复和分布式 worker 需求时，再评估 Celery、Dramatiq 或 Temporal。

---

## 6. 文档解析

当前已实现：

- PDF：PyMuPDF。
- chunk：token 近似切分，保留页码。

下一步扩展建议：

| 格式 | 建议工具 | 阶段 |
|---|---|---|
| PDF | PyMuPDF + pdfplumber | 已有，继续增强 |
| DOCX / PPTX / HTML | MarkItDown | 中期可接入，用于快速转 Markdown |
| Markdown / TXT | 原生读取或 markdown-it-py | 中期可接入 |
| HTML 正文抽取 | BeautifulSoup / trafilatura | 中期可接入 |
| 结构化多格式解析 | Unstructured | 中期评估 |
| 复杂 PDF 表格/版面/OCR | Docling | 后期升级 |
| 超广格式解析 | Apache Tika | 后期评估 |

短期不强依赖 Docling。先保证普通文档可稳定入库、chunk 和检索。

工具取舍：

- MarkItDown：适合快速把 Office、HTML 等资料转成 Markdown，作为多格式接入的轻量优先方案。
- Unstructured：适合需要文档元素类型、标题、表格、正文块等结构化信息的场景。
- Docling：适合复杂 PDF、表格、版面、公式和 OCR，但引入后解析链路更重，应后置。
- Tika：格式覆盖广，但 Java 服务化和部署成本更高，暂不优先。

---

## 7. RAG 技术栈

当前核心链路：

```text
query rewrite
  -> dense retrieval
  -> BM25 sparse retrieval
  -> RRF fusion
  -> rerank
  -> Evidence Pack
  -> answer + citations + trace
```

保留策略：

- dense retrieval 使用 Qdrant。
- sparse retrieval 当前使用 `rank-bm25`。
- fusion 使用 RRF。
- reranker 通过 provider abstraction。
- LLM 只能基于 Evidence Pack 回答。

扩展方向：

- Phase 3：支持 `knowledge_base_id` 多文档检索。
- Phase 4：trace 持久化和评测 API。
- Phase 5：Agent 多轮检索和 reviewer。
- Phase 6：如规模上升，再评估 Qdrant sparse vector、OpenSearch、Elasticsearch 或 Milvus。

检索工具取舍：

| 技术 | 当前策略 | 引入条件 |
|---|---|---|
| rank-bm25 | 短期继续使用 | 当前规模足够，便于测试 |
| Qdrant sparse vector / native hybrid | 中期评估 | BM25 计算成为性能瓶颈 |
| Elasticsearch / OpenSearch | 后期评估 | 需要强全文检索、复杂过滤、排序解释 |
| Milvus | 后期评估 | Qdrant 容量或并发不足 |
| pgvector | 暂不引入 | 当前已有 Qdrant，避免重复向量存储 |

---

## 8. 模型 Provider

继续保持 provider abstraction：

```text
LLMProvider
EmbeddingProvider
RerankerProvider
```

当前支持方向：

- LLM：OpenAI-compatible、Anthropic、local。
- Embedding：OpenAI-compatible、local sentence-transformers。
- Reranker：simple deterministic fallback。

后续建议：

- 增加真实 cross-encoder reranker provider。
- 增加模型调用耗时和 token 成本记录。
- 不在业务层直接调用模型 SDK。

### 8.1 Reranker 升级路线

| 方案 | 用途 | 策略 |
|---|---|---|
| simple fallback | 测试和无模型环境 | 保留 |
| BGE reranker | 本地或自托管重排 | 优先评估 |
| Jina reranker | 多语种重排 | 可选评估 |
| Cohere Rerank | 云端高质量 rerank | 成本可接受时评估 |
| Voyage reranker | 云端 rerank | 可选评估 |

### 8.2 模型网关

暂不引入 LiteLLM Proxy。当前 provider abstraction 已能覆盖 OpenAI-compatible、Anthropic 和 local provider。

当出现以下情况时再评估 LiteLLM：

- 同时接入多个模型供应商。
- 需要统一预算、限流和 fallback。
- 需要集中记录模型调用成本。
- 需要为多租户隔离模型 key。

---

## 9. 权限与安全

Phase 4 开始实现：

- JWT 登录。
- RBAC：系统管理员、知识库管理员、普通用户。
- 知识库级访问控制。
- 审计日志。

安全原则：

- `.env`、密钥、token 不进入 Git。
- 上传文档、网页内容、外部搜索结果均视为不可信内容。
- 检索内容不能触发工具调用。
- Agent 工具权限由后端策略控制。
- 高风险操作需要确认。

具体 auth 库暂不锁定，可先自研最小 JWT + password hashing；复杂用户管理再评估 FastAPI Users 等方案。

权限工具取舍：

| 工具 | 策略 | 引入条件 |
|---|---|---|
| 自研最小 JWT + RBAC | Phase 4 优先 | 管理员、知识库管理员、普通用户足够 |
| FastAPI Users | 可评估 | 用户注册、邮箱验证、密码重置需求增强 |
| Casbin | 后期评估 | RBAC/ABAC 规则复杂化 |
| OpenFGA | 后期评估 | 团队、共享、继承、关系型权限复杂化 |

---

## 10. Trace、评测与看板

短期自建 trace 数据模型，记录：

- trace id。
- user id / knowledge base id / session id。
- query 和 rewritten query。
- dense/sparse/fused/reranked results。
- Evidence Pack。
- final answer 和 citations。
- latency、model、token/cost。

评测指标：

- Hit Rate。
- Recall@K。
- MRR。
- Citation Accuracy。
- Faithfulness。
- Answer Relevance。
- Latency。

看板工具后置到 Phase 6，可选 ECharts 或 Recharts。

评测与观测工具取舍：

| 工具 | 用途 | 策略 |
|---|---|---|
| 自建 trace 表 | 问答与检索链路记录 | Phase 4 优先 |
| Ragas | RAG 指标评测 | 固定评测集建立后引入 |
| DeepEval | LLM-as-judge、自定义评测 | 可与 Ragas 二选一或并行试验 |
| Langfuse | LLM trace、prompt、成本、评测 | 自建 trace 不够用时引入 |
| Phoenix | OpenTelemetry 友好的 LLM 观测 | 需要标准化 tracing 时评估 |
| ECharts / Recharts | 前端统计看板 | Phase 6 引入 |

---

## 11. Agent 编排

推荐使用 LangGraph，但只在 Phase 5 引入。

Agent 边界：

```text
Planner -> Retrieval -> Analyst -> Writer -> Reviewer
```

要求：

- 固定工作流优先。
- 每一步有输入、输出、状态和 trace。
- 工具权限明确。
- 最大迭代次数明确。
- 失败时返回当前已完成结果和失败原因。

暂不引入 A2A、MCP 工具市场或完全自主 Agent。

Agent 工具取舍：

| 技术 | 策略 | 原因 |
|---|---|---|
| LangGraph | Phase 5 推荐 | 状态机式工作流，适合受控 Agent |
| LangChain Agent | 暂不作为主编排 | 容易变成开放式工具调用 |
| LlamaIndex Agent | 可参考 | 更偏数据接入和 RAG 生态 |
| Haystack Pipeline | 可参考 | pipeline 思路成熟，但不替换现有核心链路 |
| MCP | 后期工具标准化 | 当前外部工具数量不足，先不引入 |
| A2A | 长期跨系统协作 | 当前没有跨 Agent 系统集成需求 |

LangGraph 引入前置条件：

- 知识库级检索完成。
- trace 持久化完成。
- 权限和工具边界明确。
- Agent 执行失败可以记录并返回。

---

## 12. 技术变更规则

新增关键基础设施前必须说明：

- 解决什么问题。
- 为什么现有组件不能满足。
- 对部署、测试、迁移和维护的影响。

当前禁止随意替换：

- FastAPI。
- Next.js。
- PostgreSQL。
- Qdrant。
- Redis/RQ。
- provider abstraction。

可以局部扩展，但不能破坏现有 RAG 闭环。
