# ScholarPilot 开发环境配置

本文档记录 ScholarPilot 的开发环境状态与配置方法。

---

## 环境总览

| 组件 | 状态 | 位置 |
|---|---|---|
| Python | ✅ 3.13.9 (miniconda) | `D:\miniconda3\python.exe` |
| uv | ✅ 0.11.25 | `C:\Users\admin\AppData\Roaming\Python\Python313\Scripts\uv.exe` |
| Node.js | ✅ v24.14.0 | `C:\Program Files\nodejs\` |
| pnpm | ✅ 11.5.2 | 全局（PATH 可用） |
| WSL Ubuntu-22.04 | ✅ 运行中 | 数据在 `D:\WSL\Ubuntu\ext4.vhdx` |
| Docker Engine | ⏳ 待安装（WSL 内） | 安装后数据在 D 盘 vhdx 内 |
| PostgreSQL/Qdrant/Redis | ⏳ 待启动 | 通过 `docker compose` |

**关键：WSL 数据已在 D 盘**（`D:\WSL\Ubuntu\ext4.vhdx`，164G），因此 Docker 装进 WSL 后，所有容器数据、镜像、卷都天然存储在 D 盘，无需额外迁移。

---

## uv 使用说明

`uv` 不在 bash PATH 中，需用完整路径调用：

```bash
# 设置别名（每次会话）
export UV="/c/Users/admin/AppData/Roaming/Python/Python313/Scripts/uv.exe"

# 后端命令
cd D:/ScholarPilot/backend
"$UV" sync --extra dev
"$UV" run pytest
"$UV" run ruff check
"$UV" run uvicorn app.main:app --reload
```

---

## Docker Engine 安装（WSL 内）

Docker Desktop 未安装（`C:\Program Files\Docker\` 为空，仅有死链接残留）。
采用更轻量的方案：在 WSL Ubuntu-22.04 内安装 Docker Engine。

### 安装步骤

在 **Windows 终端** 执行（脚本会提示输入 sudo 密码）：

```bash
wsl -d Ubuntu-22.04 -- bash /mnt/d/ScholarPilot/scripts/install-docker-wsl.sh
```

脚本会：
1. 清理 Docker Desktop 残留的死链接（`/usr/bin/docker`、`/usr/bin/hub-tool`）
2. 添加 Docker 官方 apt 源
3. 安装 `docker-ce` + `docker-compose-plugin`
4. 将当前用户加入 `docker` 组（免 sudo）
5. 用 systemd 启用 docker 自启
6. 验证安装

### 安装后生效

```bash
# 让 docker 组生效（必须重启 WSL）
wsl --shutdown
wsl -d Ubuntu-22.04

# 验证免 sudo
docker ps
docker compose version
```

---

## 启动 ScholarPilot 基础设施

Docker 装好后，在 **WSL 内** 执行：

```bash
cd /mnt/d/ScholarPilot
docker compose up -d
docker compose ps          # 等待 postgres/qdrant/redis 变为 healthy
```

服务端口：
- PostgreSQL: `localhost:5432`
- Qdrant: `localhost:6333` (REST) / `6334` (gRPC)
- Redis: `localhost:6379`

数据卷（持久化在 D 盘 vhdx 内）：
- `postgres_data`、`qdrant_data`、`redis_data`

---

## 启动后端

```bash
cd D:/ScholarPilot/backend
export UV="/c/Users/admin/AppData/Roaming/Python/Python313/Scripts/uv.exe"

# 首次：配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 和 EMBEDDING_API_KEY

# 首次：运行数据库迁移
"$UV" run alembic upgrade head

# 启动 API
"$UV" run uvicorn app.main:app --reload

# 另开终端：启动 RQ worker（处理 PDF 上传）
"$UV" run rq worker --url "redis://localhost:6379/0" default
```

---

## 启动前端

```bash
cd D:/ScholarPilot/frontend
pnpm dev
# 打开 http://localhost:3000
```

---

## 端到端验证流程

1. `docker compose up -d`（WSL 内）
2. `alembic upgrade head`（建表）
3. `uvicorn` 启动 API（:8000）
4. `rq worker` 启动 worker
5. `pnpm dev` 启动前端（:3000）
6. 浏览器：上传 PDF → 等 status=indexed → 提问 → 看答案和引用

---

## 常见问题

### `docker` 命令在 Windows 终端不可用
Docker 装在 WSL 内，**必须在 WSL 终端里执行 docker 命令**。Windows 侧没有 docker CLI。

### WSL 重启后 docker 没启动
确认 systemd 已启用（`/etc/wsl.conf` 里 `[boot] systemd=true`）。脚本已用 `systemctl enable docker` 配置自启。

### 端口冲突
PostgreSQL(5432)/Qdrant(6333)/Redis(6379) 端口若被占用，修改 `docker-compose.yml` 的端口映射。
