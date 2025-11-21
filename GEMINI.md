# AuthHub Project Context

## Project Overview
AuthHub is an enterprise-grade SSO (Single Sign-On) and Unified Permission Platform designed for Feishu (Lark) integration. It employs a decentralized architecture for permission verification, ensuring high performance and availability by allowing local token and permission checks within business systems.

## Tech Stack

### Backend
*   **Language:** Python 3.11+
*   **Framework:** FastAPI
*   **Database:** PostgreSQL (SQLAlchemy 2.0 + Alembic)
*   **Cache/Message Broker:** Redis (used for caching permissions and Pub/Sub for real-time updates)
*   **Authentication:** OAuth2 (Feishu), JWT (RS256)
*   **Package Manager:** `uv`

### Frontend
*   **Framework:** React 18 + TypeScript
*   **UI Library:** Ant Design 5
*   **State Management:** Zustand + React Query
*   **Build Tool:** Vite
*   **Package Manager:** `pnpm`

### SDKs
*   **Python:** `authhub-sdk` (Supports FastAPI, Flask, Django)
*   **TypeScript:** `@authhub/sdk` (Supports React, Vue, Node.js)

## Project Structure

```text
AuthHub/
├── backend/                # Python FastAPI Backend
│   ├── app/                # Application Source Code
│   │   ├── auth/           # Authentication Logic (Feishu, JWT)
│   │   ├── core/           # Core configs, DB, Cache, Security
│   │   ├── models/         # SQLAlchemy Models
│   │   ├── rbac/           # Role-Based Access Control Logic
│   │   └── ...
│   ├── alembic/            # Database Migrations
│   ├── scripts/            # Utility scripts (Key generation)
│   └── pyproject.toml      # Backend Dependencies & Config
├── frontend/               # React Admin Console
│   ├── src/                # Source Code
│   └── package.json        # Frontend Dependencies
├── sdk/                    # Client SDKs
│   ├── python/             # Python SDK Source & Examples
│   └── typescript/         # TypeScript SDK Source & Examples
├── docs/                   # Documentation
├── docker/                 # Docker Containers
└── scripts/                # Global Utility Scripts (Publishing, etc.)
```

## Key Development Commands

### Backend (`/backend`)
*   **Install Dependencies:** `uv sync`
*   **Activate Environment:** `source .venv/bin/activate` (or use `uv run`)
*   **Start Server:** `uvicorn app.main:app --reload` (or `uv run uvicorn ...`)
*   **Database Migration:** `uv run alembic upgrade head`
*   **Generate RSA Keys:** `python scripts/generate_keys.py`
*   **Lint/Format:** `ruff check .`, `black .`, `mypy .`
*   **Test:** `pytest`

### Frontend (`/frontend`)
*   **Install Dependencies:** `pnpm install`
*   **Start Dev Server:** `pnpm dev`
*   **Build for Production:** `pnpm build`
*   **Lint:** `pnpm lint`
*   **Format:** `pnpm format`

### SDK - Python (`/sdk/python`)
*   **Build:** `uv build --no-sources`
*   **Publish:** Use `../../scripts/publish-python.sh [test|prod]`
*   **Test:** `pytest tests/`

### SDK - TypeScript (`/sdk/typescript`)
*   **Build:** `pnpm build` (uses `tsup`)
*   **Dev:** `pnpm dev`
*   **Test:** `pnpm test` (uses `jest`)

## Development Conventions
*   **Package Management:** Strict preference for `uv` (Python) and `pnpm` (Node.js).
*   **Code Style:**
    *   Python: Follows `black` and `ruff` configuration in `pyproject.toml`. Type hinting is enforced (`mypy`).
    *   TypeScript: Follows `eslint` and `prettier`.
*   **Architecture:**
    *   **Decentralized Verification:** SDKs verify tokens locally using public keys and cached permissions to minimize network overhead.
    *   **Syncing:** Permissions are synced via Redis Pub/Sub and periodic polling.
*   **Documentation:** Extensive documentation in `docs/` and `README.md` files in each subdirectory.
