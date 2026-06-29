# ScholarPilot 开发环境配置

本文档记录 ScholarPilot 的开发环境状态与配置方法。

---

## 环境总览（当前实际状态）

| 组件 | 状态 | 位置 / 说明 |
|---|---|---|
| Python (Windows) | ✅ 3.13.9 (miniconda) | `D:\miniconda3\python.exe` |
| uv (Windows) | ✅ 0.11.25 | `C:\Users\admin\AppData\Roaming\Python\Python313\Scripts\uv.exe` |
| Node.js | ✅ v24.14.0 | `C:\Program Files\nodejs\` |
| pnpm | ✅ 11.5.2 | 全局（PATH 可用） |
| WSL Ubuntu-22.04 | ✅ 运行中 | 数据在 `D:\WSL\Ubuntu\ext4.vhdx`（164G） |
| uv (WSL) | ✅ 0.11.25 | `~/.local/bin/uv`（WSL 内） |
| Python (WSL) | ✅ 3.12.13 | uv 自动下载，WSL venv `.venv-wsl` |
| Docker Engine | ✅ 29.6.1 + compose 5.2.0 | 装在 WSL Ubuntu 内，数据在 D 盘 |
| PostgreSQL/Qdrant/Redis | ✅ Docker 容器运行中 | 端口 5432/6333/6379 |

**关键：WSL 数据已在 D 盘**（`D:\WSL\Ubuntu\ext4.vhdx`），Docker 数据天然在 D 盘，无需迁移。

---

## 架构：API 在 Windows，Worker 在 WSL

由于 **RQ worker 依赖 `os.fork()`，Windows 不支持**，采用分离部署：

| 服务 | 运行环境 | 原因 |
|---|---|---|
| FastAPI API | Windows (uvicorn) | 无 fork 依赖，热重载方便 |
| RQ Worker | WSL Ubuntu (Linux) | RQ 需要 `os.fork()` |
| PostgreSQL/Qdrant/Redis | WSL Docker | 统一基础设施 |

API 和 Worker 共享同一个 PostgreSQL（Docker），文件路径用 **POSIX 相对路径**（`storage/xxx.pdf`）存储，确保跨平台兼容。

---

## uv 使用说明

### Windows 侧（API）

`uv` 不在 bash PATH，需用完整路径：

```bash
export UV="/c/Users/admin/Appdata/Roaming/Python/Python313/Scripts/uv.exe"
export UV_LINK_MODE=copy   # 避免 hardlink 警告

cd D:/ScholarPilot/backend
"$UV" sync --extra dev
"$UV" run uvicorn app.main:app --reload
```

### WSL 侧（Worker）

```bash
wsl -d Ubuntu-22.04
export PATH="$HOME/.local/bin:$PATH"
cd /mnt/d/ScholarPilot/backend
UV_PROJECT_ENVIRONMENT=.venv-wsl uv sync --extra dev --python 3.12
```

---

## Docker（已安装完成）

Docker Engine 装在 WSL Ubuntu-22.04 内（非 Docker Desktop）。
- 镜像加速器已配置（`/etc/docker/daemon.json`）：`docker.1ms.run`、`docker.xuanyuan.me`、`docker.m.daocloud.io`
- systemd 自启已启用
- 用户 `ykl` 已加入 docker 组

**注意**：docker 命令必须在 WSL 内执行，Windows 侧无 docker CLI。

### 常用命令（WSL 内）

```bash
cd /mnt/d/ScholarPilot
docker compose up -d        # 启动 postgres + qdrant + redis
docker compose ps           # 查看状态
docker compose down         # 停止（保留数据）
docker compose down -v      # 停止并删除数据卷
docker compose logs -f      # 查看日志
```

### 端口冲突处理（已完成）

WSL 内原有的本地 PostgreSQL 14 和 Redis 已停止并禁用自启（`systemctl disable`），避免与 Docker 容器端口冲突。如需恢复，重新 `systemctl enable`。

---

## 启动 ScholarPilot（完整流程）

### 1. 启动基础设施（WSL 内）

```bash
wsl -d Ubuntu-22.04
cd /mnt/d/ScholarPilot
docker compose up -d
docker compose ps    # 等待三个服务 healthy
```

### 2. 配置 API key（首次）

```bash
cd D:/ScholarPilot/backend
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 和 EMBEDDING_API_KEY
```

### 3. 运行数据库迁移（首次，Windows 侧）

```bash
export UV="/c/Users/admin/Appdata/Roaming/Python/Python313/Scripts/uv.exe"
cd D:/ScholarPilot/backend
"$UV" run alembic upgrade head
```

### 4. 启动 API（Windows 侧）

```bash
"$UV" run uvicorn app.main:app --reload    # :8000
```

### 5. 启动 RQ Worker（WSL 侧，另开终端）

```bash
wsl -d Ubuntu-22.04
export PATH="$HOME/.local/bin:$PATH"
cd /mnt/d/ScholarPilot/backend
UV_PROJECT_ENVIRONMENT=.venv-wsl uv run rq worker --url "redis://localhost:6379/0" default
```

### 6. 启动前端（Windows 侧）

```bash
cd D:/ScholarPilot/frontend
pnpm dev    # :3000
```

### 7. 端到端验证

浏览器打开 http://localhost:3000：
1. 上传 PDF → 等 status=indexed
2. 提问 → 看答案和引用

---

## 已验证的端到端流程

- ✅ Docker 三服务启动（postgres/qdrant/redis healthy）
- ✅ Alembic 迁移建表（documents/chunks/citations）
- ✅ API 启动（/health, /documents, /docs）
- ✅ PDF 上传 → 解析（status: parsed, pages: 4）
- ✅ Qdrant chunks 集合创建
- ⏳ Embedding + 问答：**需要配置 LLM/Embedding API key**

---

## 常见问题

### `docker` 命令在 Windows 终端不可用
Docker 装在 WSL 内，**必须在 WSL 终端执行 docker 命令**。

### RQ worker 报 `os.fork` 错误
Worker 必须在 WSL（Linux）跑，不能在 Windows 跑。

### 文件路径错误（worker 找不到 PDF）
文件路径已改为 POSIX 相对路径（`storage/xxx.pdf`）。API 和 worker 都从 backend 目录解析。不要改回绝对路径。

### WSL 重启后 docker 没启动
systemd 已启用，docker 已 `systemctl enable`。若没起来，手动 `sudo systemctl start docker`。

### 端口冲突（5432/6379）
WSL 内本地 PostgreSQL/Redis 已禁用。若仍冲突，检查 `ss -tlnp | grep <port>`。
