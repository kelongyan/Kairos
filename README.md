# ScholarPilot

ScholarPilot is a browser-based AI Research Copilot for paper reading, evidence-first retrieval, citation-grounded question answering, and research workflow assistance.

The project is currently in the planning and foundation stage. The first implementation goal is a stable single-paper RAG MVP:

```text
Upload PDF -> Parse -> Chunk -> Embed -> Retrieve -> Answer -> Return citations
```

---

## Current Direction

ScholarPilot will be built first as a Web Research Workspace:

```text
Next.js Web UI
  -> FastAPI Backend
  -> PostgreSQL / Qdrant / Redis
  -> RAG Pipeline / Agent Workflow
  -> LLM / Embedding / Reranker Providers
```

Desktop packaging is not a Phase 1 goal. If needed later, it should wrap the Web UI and local backend instead of changing the core architecture.

---

## Documentation

Read the documents in this order:

| Order | Document | Purpose |
|---|---|---|
| 1 | [RULE.md](RULE.md) | Project rules, development constraints, Git rules, testing requirements |
| 2 | [doc/01-project-overview.md](doc/01-project-overview.md) | Product vision, architecture, core modules, risks |
| 3 | [doc/02-development-roadmap.md](doc/02-development-roadmap.md) | Phased development plan and acceptance criteria |
| 4 | [doc/03-technology-stack.md](doc/03-technology-stack.md) | Technology choices, alternatives, adoption phases |
| 5 | [doc/04-development-progress.md](doc/04-development-progress.md) | Phase status and progress log |
| 6 | [doc/05-environment-setup.md](doc/05-environment-setup.md) | Dev environment setup (uv, pnpm, Docker in WSL) |

---

## Repository Structure

```text
ScholarPilot/
├─ README.md
├─ RULE.md
└─ doc/
   ├─ 01-project-overview.md
   ├─ 02-development-roadmap.md
   ├─ 03-technology-stack.md
   └─ 04-development-progress.md
```

Application code will be created in Phase 0.

Planned structure:

```text
ScholarPilot/
├─ backend/
├─ frontend/
├─ doc/
├─ README.md
└─ RULE.md
```

---

## Recommended Technology Stack

The initial stack is defined in [doc/03-technology-stack.md](doc/03-technology-stack.md).

Summary:

```text
Frontend:
Next.js + React + TypeScript + pnpm + Tailwind CSS + shadcn/ui + TanStack Query + PDF.js

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
```

---

## Phase Plan

Detailed roadmap: [doc/02-development-roadmap.md](doc/02-development-roadmap.md)

| Phase | Goal |
|---|---|
| Phase 0 | Project foundation |
| Phase 1 | Single-paper RAG MVP |
| Phase 2 | High-quality Hybrid RAG |
| Phase 3 | Research workflow |
| Phase 4 | Trend tracking and knowledge enhancement |
| Phase 5 | Productization and deployment |

---

## Current Status

Current phase:

```text
Phase 0: Not Started
```

Current priority:

```text
Project foundation -> backend health check -> frontend shell -> basic tests -> local development commands
```

---

## Development Rules

Before development:

- Read [RULE.md](RULE.md).
- Follow the technology stack in [doc/03-technology-stack.md](doc/03-technology-stack.md).
- Follow the phase plan in [doc/02-development-roadmap.md](doc/02-development-roadmap.md).
- Update [doc/04-development-progress.md](doc/04-development-progress.md) when a phase is completed.

Each completed phase must be:

- implemented,
- verified,
- documented,
- committed,
- pushed to GitHub.

---

## GitHub

Repository:

```text
https://github.com/kelongyan/ScholarPilot
```
