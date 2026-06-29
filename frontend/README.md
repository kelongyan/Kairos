# Kairos Frontend

Next.js web UI for Kairos, a verifiable team knowledge-base Q&A and knowledge
operations platform. The current interface is a three-column workspace with a
document library, chat area, and citation / evidence panel. The next product
phase adds knowledge-base selection, multi-document Q&A, and feedback signals.

## Requirements

- Node.js 20+
- [pnpm](https://pnpm.io/) (do **not** use npm — see project RULE.md §8.2)

## Setup

```bash
cd frontend
pnpm install
```

## Run

```bash
pnpm dev
```

Open http://localhost:3000.

## Lint and build

```bash
pnpm lint
pnpm build
```

## Configuration

Copy `.env.example` to `.env.local` and adjust the backend URL if needed:

```bash
cp .env.example .env.local
```
