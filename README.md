---
title: GOAT-Evolution
emoji: ⚔️
colorFrom: red
colorTo: blue
sdk: docker
app_port: 7860
tags:
  - openenv
  - reinforcement-learning
  - ai-safety
  - self-improvement
  - multi-agent
license: mit
---

# GOAT-Evolution ⚔️

Autonomous co-evolving AI safety red-teaming environment.

## Links

- Live Space: `https://kyoiske-goat-evolution.hf.space`
- Training Notebook: `training/colab_training.ipynb`
- Unsloth Notebook: `training/unsloth_finetune.ipynb`
- Baseline Scores: `training/baseline_scores.json`

## Problem

Safety red-teaming is still mostly manual. GOAT-Evolution trains attacker and defender agents in a deterministic OpenEnv-compatible loop so they can discover and patch vulnerabilities automatically.

## What We Built

- Red attacker and Blue defender agents with pluggable providers (HF, NVIDIA NIM, OpenAI, Gemini, Scripted fallback)
- Deterministic simulator + judge + reward + novelty scoring
- Auto-growing vulnerability registry (`backend/data/vulnerability_registry.json`)
- Cinematic React UI (Battle Arena, Registry Explorer, Analytics, Settings)
- OpenEnv routes plus custom battle/registry/metrics APIs and WebSocket stream
- Textual TUI bonus (`python -m tui.app`)

## Baseline vs Trained (placeholder rows)

| Metric | Scripted Baseline | Trained |
|---|---:|---:|
| Task 4 ASR | 0.42 | TBD |
| Task 5 Red Score | 0.30 | TBD |
| Task 6 Cycle Score | 0.38 | TBD |

## Local Setup

```bash
cp .env.example .env.local
docker compose up --build
```

No-Docker dev:

```bash
uv sync
uv run uvicorn backend.server.app:app --reload --port 7860
cd frontend
npm install
npm run dev
```

## Validate OpenEnv Compatibility

```bash
make validate
```
