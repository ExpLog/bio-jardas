# Bio Jardas

Discord bot for the Aveiro Discord community.

## Project Overview

* **Technology Stack**: Python-based Discord bot using the `disnake` library.
* **Package Management**: Managed with `uv`.
* **Architecture**: Domain-Driven Design (DDD) located in `bio_jardas/domains/`.
* **Dependency Injection**: Uses `dishka` (defined in `bio_jardas/dependency_injection.py`).
* **Database**: PostgreSQL managed by `SQLAlchemy` (asyncio) and `Alembic` for migrations.
* **Observability**: Uses `structlog` for logging.

## Architecture & Project Structure

The project follows a Domain-Driven Design (DDD) approach. Each domain in `bio_jardas/domains/` is self-contained and typically includes:

* **`models.py`**: SQLAlchemy models.
  * Inherit from `Base` (in `bio_jardas/db/models.py`) for standard tables (includes `id`).
  * Inherit from `AuditBase` for tables requiring `created_at`, `updated_at`, `created_by`, and `updated_by`.
* **`repositories.py`**: Data access layer.
  * Inherit from `Repository` or `CRUDRepository` (in `bio_jardas/db/repositories.py`).
  * `CRUDRepository` provides standard methods (`get_by_id`, `add`, `delete`, etc.) and requires setting `model_type`.
* **`services.py`**: Business logic layer.
  * Orchestrates multiple repositories and handles domain-specific logic.
  * This is the primary layer for calculating points, rolls, and complex interactions.
* **`cogs.py`**: Entry points for Discord interactions (Slash commands, Listeners).
  * Inherit from `BaseCog`.
  * Responsible for parsing Discord input, calling services, and sending responses/emojis.
* **`objects.py` / `dtos.py` / `enums.py`**: Data Transfer Objects and domain-specific constants.

### Dependency Flow
Dependencies flow one way: **Cog -> Service -> Repository -> Session**.
All wiring is handled by `dishka` in `bio_jardas/dependency_injection.py`.

## Domain Overview

* **`config`**: Global bot settings (e.g., reply intensity).
* **`message`**: The core engine for bot responses. Handles message groups, weighted rolls for channel/user replies, and dynamic handlers like `caralhamos`.
* **`game`**: Tracking scores and streaks for mini-games (e.g., Russian Roulette).
* **`time_gate`**: Manages cooldowns and timed restrictions (e.g., self-bans or feature lockouts).
* **`schedule`**: Orchestrates background tasks using `apscheduler`, such as event reminders and periodic messages.

### Key Relationships
* **`message` & `config`**: `MessageService` (via Cogs) checks `ConfigService` for global intensity before replying.
* **`schedule` & `message`**: Scheduled jobs use `MessageService` to fetch random messages from specific groups for periodic announcements.
* **`game` & `time_gate`**: Games like roulette interact with `time_gate` to apply temporary "bans" or cooldowns on failure.

## Configuration

The bot uses `pydantic-settings` for configuration, defined in `bio_jardas/settings.py`. It expects a `.env` file with the following nested structure (using `_` as a delimiter):

* **Discord**: `DISCORD_TOKEN`
* **Postgres**: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DATABASE`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
* **Game**: `GAME_SHADOW_BAN_ROLE`, `GAME_MEMBER_ROLE`

## ETL & Data Seeding

The `etl/` directory contains scripts for initial data loading.
* **`etl/load_messages.py`**: A CLI tool (using `cyclopts` and `pandas`) to seed an empty database with message groups and messages from a CSV.
  * Run with: `uv run --group etl python etl/load_messages.py path/to/messages.csv`

## Testing

* **Status**: The project uses `pytest` and `pytest-asyncio` for automated testing.
* **Running Tests**: Use `make py/test` to run the test suite.
* **Verification**: Changes should be verified with automated tests in `tests/` whenever possible. Manual verification in a development Discord server is still recommended for Cog-level interactions.
* **Philosophy**:
  * **High-Fidelity**: Never mock the database or use a different engine (like SQLite). Always use the project's real PostgreSQL instance running in local Docker.
  * **Isolation**: Every test must run within a transaction that is rolled back at the end to ensure the database remains clean.
  * **Execution**: Always use `uv run -m pytest tests/` (or `make py/test`) to ensure correct Python module discovery.
  * **Async Tests**: Do NOT use the `@pytest.mark.asyncio` decorator. The project is configured with `asyncio_mode = "auto"`, which automatically handles all `async def` tests and fixtures.

## Building and Running

### Development Environment

* **Install Dependencies**: Use `make py/install` (which runs `uv sync`).
* **Environment Variables**: The bot expects a `.env` file. Initialize by copying `.env.sample` if it's missing or updated.

### Commands

Key tasks should be performed using the project's `Makefile`:

* **Python/Formatting**:
  * `make py/install`: Sync dependencies via `uv`.
  * `make py/fmt`: Format and fix linting issues using `ruff`.
  * `make py/lint`: Check for linting and formatting issues.
  * `make py/test`: Run the test suite.
  * `make py/ipython`: Start an interactive `ipython` session with `.ipython_startup.py`.
* **Database**:
  * `make db/revision m="description"`: Create a new Alembic migration.
  * `make db/upgrade`: Upgrade the database to the latest revision.
  * `make db/downgrade revision="rev"`: Downgrade to a specific revision.
* **Docker**:
  * `make docker/up`: Start the PostgreSQL service.
  * `make docker/down`: Stop services.
  * `make docker/downv`: Stop services and remove volumes.

## Development Conventions

* **Tooling**: Always prefer `uv run` and the project's `Makefile` targets. Never invoke `python`, `pip`, or `alembic` directly. Use `uv add` to manage dependencies.
* **Domain Structure**: When adding new features, follow the existing domain pattern in `bio_jardas/domains/<domain_name>/`:
  * `models.py`: SQLAlchemy models.
  * `repositories.py`: Data access logic.
  * `services.py`: Business logic.
  * `cogs.py`: Disnake slash commands and event handlers.
  * `enums.py`, `objects.py`, `dtos.py`: Supporting types.
* **Cog Development**:
  * Inherit from `BaseCog` (in `bio_jardas/cogs.py`).
  * Use `@skip_bots_and_commands` (from `bio_jardas/decorators.py`) for `on_message` listeners to ignore bots and valid bot commands.
* **Dependency Injection**: Uses `dishka` (defined in `bio_jardas/dependency_injection.py`).
  * **Mandatory Decorators**:
    * In **Cogs**: Use `@cog_inject` on command or listener methods.
    * In **Jobs**: Use `@job_inject` on job functions.
  * **Type Hinting**: Dependencies MUST be keyword-only arguments and type-hinted using `FromDishka[DependencyType]`.
  * **Providers**: Adding new dependencies requires updating `bio_jardas/dependency_injection.py` with appropriate `@provide` methods in the relevant `Provider` class.
* **Observability**:
  * Use `structlog` for logging. Get logger via `structlog.stdlib.get_logger()`.
  * Bind context variables using `bind_contextvars(...)` (from `structlog.contextvars`).
  * Use project-specific helpers like `bind_command_context_to_logs(context)` or `bind_listener_context_to_logs(context)` for consistent logging metadata.
* **Standards**:
  * **PEP8**: All code must strictly follow PEP8 conventions. Run `make py/fmt` and `make py/lint` before submitting any changes.
* **Migrations**: Always use `make db/revision` for schema changes.
* **Error Handling**: Differentiate between user-facing errors (which may be ignored or signaled via emoji) and internal errors in logs using `structlog`. Use the `emojis` module for consistent feedback.
