# ScholarPilot 本地模型部署

---

## 1. 部署目的

ScholarPilot RAG 流水线需要两个核心模型：

- **LLM** — 用于答案生成、查询改写、引文验证。
- **Embedding** — 用于文档分块向量化与语义检索。

在开发与本地测试阶段使用本地部署的模型，可以避免：
- 外部 API 调用的网络延迟
- Token 计费成本
- 依赖云端服务的可用性风险

同时保持对 [Ollama](https://ollama.ai) OpenAI-compatible API 的兼容性，使后端 Provider 层无需修改即可切换为云端模型。

---

## 2. 硬件环境

| 组件 | 规格 |
|---|---|
| GPU | NVIDIA RTX 3090 (24GB VRAM) |
| 存储 | `D:\Ollama\models` (9.72 GB 已用) |
| 系统 | Windows 11 |

**容量评估：**

| 模型 | VRAM 预估 | 说明 |
|---|---|---|
| Qwen3-14B (Q4_K_M) | ~9–10 GB | 14.8B 参数 + KV cache |
| BGE-M3 (F16) | ~1.5 GB | 566M 参数 |
| **合计** | **~11.5 GB** | 可同时加载，剩余 ~12.5 GB 用于 KV cache 和其他进程 |

RTX 3090 24GB 可同时运行两模型，无需卸载切换。

---

## 3. 模型选择依据

依据 `doc/03-technology-stack.md` §10.2 和 §10.3 的推荐：

| 用途 | 模型 | 理由 |
|---|---|---|
| LLM | **Qwen3-14B** | 中英文双强、学术文本支持好、工具调用/思考模式原生支持、14B Q4_K_M 可装入 24GB |
| Embedding | **BGE-M3** | 中英文混合检索强、本地部署便利、1,024 维与 Qdrant 兼容 |

### 替代方案

| 模型 | 优点 | 缺点 |
|---|---|---|
| DeepSeek-V3 / R1 | 推理能力强 | 671B MoE 无法本地运行 |
| Qwen3-32B | 效果更好 | Q4 仍超 24GB，需流式卸载 |
| BGE-EN-ICL / E5 | 英文检索强 | 中文混合场景不如 BGE-M3 |
| Qwen3 Embedding (local) | 生态一致 | 暂不支持 Ollama |

**当云端服务可用时可切换为：** Qwen-Max / DeepSeek-V3 / OpenAI GPT-4o（LLM），OpenAI text-embedding-3-large / Qwen3 Embedding（Embedding）。

---

## 4. 部署架构

```text
Windows Host
├── Ollama Server (localhost:11434)
│   ├── qwen3:14b      → LLM 生成
│   └── bge-m3:latest  → Embedding
└── ScholarPilot Backend
    ├── LLMProvider (OpenAI-compatible client)
    │   └── base_url = http://localhost:11434/v1
    └── EmbeddingProvider (OpenAI-compatible client)
        └── base_url = http://localhost:11434/api/embed
```

Backend Provider 层通过 OpenAI-compatible API 调用 Ollama，`base_url` 指向 `http://localhost:11434`。切换到云端模型时只需修改 `base_url` 和 `api_key`，业务代码无需改动。

---

## 5. 安装与配置

### 5.1 安装 Ollama

从 [ollama.ai](https://ollama.ai) 下载 Windows 安装包。

安装后版本：

```powershell
ollama --version
# ollama version is 0.30.11
```

### 5.2 配置模型存储路径

Ollama 默认模型存储在 `C:\Users\<user>\.ollama\models`。为节省 C 盘空间，迁移至 D 盘：

```powershell
# 设置用户级环境变量
[System.Environment]::SetEnvironmentVariable(
    "OLLAMA_MODELS", "D:\Ollama\models", "User"
)
```

设置后重启 Ollama 服务。后续所有模型文件下载至 `D:\Ollama\models\blobs\`。

### 5.3 拉取模型

```powershell
# LLM
ollama pull qwen3:14b

# Embedding
ollama pull bge-m3:latest
```

验证：

```powershell
ollama list
```

### 5.4 启动与持久化

Ollama 安装后默认注册为 Windows 用户级服务，开机自启。确认运行状态：

```powershell
# 查看进程
Get-Process ollama

# API 健康检查
curl.exe http://localhost:11434/api/tags
```

---

## 6. 模型详情

### 6.1 Qwen3-14B

| 属性 | 值 |
|---|---|
| 模型名 | `qwen3:14b` |
| 架构 | Qwen3 |
| 参数量 | 14,768,307,200 (14.8B) |
| 量化 | Q4_K_M (file_type 15) |
| 上下文长度 | 40,960 tokens |
| Embedding 维度 | 5,120 |
| 层数 | 40 |
| 注意力头 | 40 (8 KV heads, GQA) |
| FFN 维度 | 17,408 |
| RoPE 频率基数 | 1,000,000 |
| 特殊 Token | BOS=151643, EOS=151645 |
| 能力 | `completion`, `tools`, `thinking` |
| 磁盘占用 | ~9.28 GB |

### 6.2 BGE-M3

| 属性 | 值 |
|---|---|
| 模型名 | `bge-m3:latest` |
| 架构 | BERT |
| 参数量 | 566.70M |
| 量化 | F16 |
| 上下文长度 | 8,192 tokens |
| Embedding 维度 | 1,024 |
| 能力 | `embedding` |
| 磁盘占用 | ~1.16 GB |

---

## 7. API 接口

Ollama 提供两个兼容模式：

### 7.1 LLM 生成 (OpenAI-compatible `/v1/chat/completions`)

```powershell
curl.exe http://localhost:11434/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"qwen3:14b\",\"messages\":[{\"role\":\"user\",\"content\":\"Explain RAG in one sentence\"}]}'
```

### 7.2 Embedding (OpenAI-compatible `/v1/embeddings`)

```powershell
curl.exe http://localhost:11434/v1/embeddings `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"bge-m3:latest\",\"input\":\"RAG is a technique for knowledge-grounded generation\"}'
```

### 7.3 Ollama 原生 API

```powershell
# 生成
curl.exe http://localhost:11434/api/generate `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"qwen3:14b\",\"prompt\":\"Hello\",\"stream\":false}'

# 嵌入
curl.exe http://localhost:11434/api/embed `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"bge-m3:latest\",\"input\":\"Hello world\"}'
```

---

## 8. 后端集成配置

在 `.env` 中配置：

```env
# LLM — Ollama 本地
LLM_PROVIDER=openai
LLM_MODEL=qwen3:14b
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama  # Ollama 忽略 key，但不能为空

# Embedding — Ollama 本地
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_BASE_URL=http://localhost:11434/v1
EMBEDDING_API_KEY=ollama
EMBEDDING_DIM=1024
```

切换到云端模型时只需修改以上配置项。例如切换到 DeepSeek-V3：

```env
LLM_PROVIDER=openai
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=sk-xxxxx
```

---

## 9. 常用运维命令

```powershell
# 查看模型列表
ollama list

# 查看模型磁盘占用
Get-ChildItem -Path "D:\Ollama\models" -Recurse -File |
  Measure-Object -Property Length -Sum |
  Select-Object Count, @{N="TotalGB";E={[math]::Round($_.Sum/1GB, 2)}}

# 删除模型
ollama rm <model-name>

# 更新模型
ollama pull <model-name>

# 查看 Ollama 日志（Troubleshooting）
# Ollama 日志输出至启动它的终端，或查看 Windows Event Viewer
```

---

## 10. 注意事项

### 10.1 内存与显存

- Qwen3-14B (Q4_K_M) 在 24GB 显存下可与 BGE-M3 同时驻留。
- 首次加载模型需约 10–30 秒（加载权重至显存），后续请求延迟在可接受范围内。
- 如需释放显存，可使用 `ollama stop` 或等待模型超时卸载（默认 5 分钟无请求后自动卸载）。

### 10.2 API Key

Ollama 的 OpenAI-compatible API 不验证 key。配置中 `LLM_API_KEY` 和 `EMBEDDING_API_KEY` 设为任意非空字符串即可。在生产部署中切换至云端服务时需替换为真实 key。

### 10.3 模型更新

Ollama 模型标签（如 `qwen3:14b`）可能随上游更新。使用 `ollama pull` 拉取最新版本。若需固定版本，使用具体标签（如 `qwen3:14b-q4_K_M`）。当前拉取时间：2026-06-29。

### 10.4 网络隔离

本地模型运行在 `localhost:11434`，无外部网络依赖。在离线开发环境中仍可正常工作。

### 10.5 端到端验证

```powershell
# 1. 确认 Ollama 运行
curl.exe http://localhost:11434/api/tags

# 2. 测试 LLM
curl.exe http://localhost:11434/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"qwen3:14b\",\"messages\":[{\"role\":\"user\",\"content\":\"Hi\"}]}'

# 3. 测试 Embedding
curl.exe http://localhost:11434/v1/embeddings `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"bge-m3:latest\",\"input\":\"test\"}'
```

---

## 11. 未来扩展

| 阶段 | 计划 | 时间 |
|---|---|---|
| Phase 2 | 增加本地 Reranker 模型（BGE Reranker v2 / Qwen3 Reranker），提升检索质量 | 后续阶段 |
| Phase 3+ | 评估 vLLM / llama.cpp server 替换 Ollama（更高吞吐、更细粒度控制） | 后续阶段 |
| Phase 3+ | 评估 Qwen3-32B 是否需要 2×RTX 3090 或流式卸载方案 | 后续阶段 |

---

*文档版本: 2026-06-29*
*部署人: AI Assistant (ScholarPilot)*
