# Team Workspace Invitation & RBAC Engine

A robust backend service designed to manage team workspaces, granular role-based access control (RBAC), and secure invitation workflows. Built for production environments with asynchronous operations, strict validation, and high extensibility.

---

## Features

- **Granular RBAC**: Role-based permissions mapped cleanly to resources and endpoints.
- **Secure Invitation Workflows**: Token-based invitations with expiration handling and email dispatching.
- **Multi-Tenant Workspace Isolation**: Isolate resources and team members securely per workspace.
- **Asynchronous Architecture**: High-performance non-blocking I/O operations.
- **Strict Data Validation**: Robust request and response validation layers.

---

## Tech Stack

- **Language**: Python 3.14+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation & Settings**: Pydantic v2
- **Database & ORM**: SQLAlchemy (Async) with Data Access Object (DAO) patterns

---

## Project Structure

```text
├── src/
│   ├── api/            # FastAPI routers and endpoints
│   ├── core/           # Configuration, security, and database sessions
│   ├── dao/            # Data Access Objects for database operations
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic data validation schemas
│   └── services/       # Business logic layer
├── alembic/            # Database migrations
├── tests/              # Test suite
├── main.py             # Application entry point
├── requirements.txt    # Project dependencies
└── README.md

