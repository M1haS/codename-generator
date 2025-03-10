# 🕵️ Codename Generator API

A production-grade REST API for generating, tracking and managing operation codenames — like intelligence agencies do, but with a swagger UI.

## Features

- 🎲 **Generation engine** — combines adjective + noun wordlists with configurable styles (military / nature / abstract / cosmic)
- 🔁 **Collision detection** — guarantees uniqueness within a namespace (project, org, team)
- 📋 **Assignment tracking** — link codenames to entities (person, project, operation) with metadata
- 📊 **Usage analytics** — most popular styles, namespace saturation, generation rate
- ♻️ **Recycle policy** — retired codenames re-enter the pool after configurable cooldown
- 🌍 **i18n wordlists** — EN / RU / DE included

## Tech Stack

- **FastAPI** — async REST
- **SQLAlchemy 2.0** (async) — ORM
- **Pydantic v2** — validation
- **aiosqlite** — lightweight default DB
- **Uvicorn** — ASGI server

## Quick Start

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync
uv run uvicorn app.main:app --reload
```

API docs → http://localhost:8000/docs

## Project Structure

```
codename-generator/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── core/
│   │   ├── wordlists.py       # curated word banks per style/lang
│   │   └── generator.py       # generation + collision logic
│   ├── models/models.py
│   ├── schemas/schemas.py
│   ├── routers/
│   │   ├── codenames.py
│   │   ├── namespaces.py
│   │   └── stats.py
│   └── services/
│       └── recycle.py
└── tests/
    ├── test_generator.py
    └── test_collision.py
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate` | Generate one or more codenames |
| GET | `/codenames` | List all assigned codenames |
| GET | `/codenames/{id}` | Get codename detail |
| POST | `/codenames/{id}/retire` | Retire a codename |
| GET | `/namespaces` | List namespaces |
| POST | `/namespaces` | Create namespace |
| GET | `/namespaces/{ns}/saturation` | % of pool used |
| GET | `/stats/styles` | Usage breakdown by style |
| GET | `/stats/timeline` | Generation rate over time |

## Generation Styles

| Style | Example |
|-------|---------|
| `military` | IRON FALCON, SILENT THUNDER |
| `nature` | EMBER FOX, DRIFT PINE |
| `abstract` | VOID SIGNAL, NULL ECHO |
| `cosmic` | DARK NEBULA, BINARY PULSE |

---

> *"The name of an operation should not reflect its purpose."* — Winston Churchill
