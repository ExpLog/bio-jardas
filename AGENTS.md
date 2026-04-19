# AGENTS.md

Guidance for AI coding agents (Claude Code, Gemini CLI, etc.) working in this repository. `CLAUDE.md` and `GEMINI.md` both import this file.

## Project

Bio Jardas is a Discord bot for the Aveiro Discord community.

* **Language / runtime**: Python 3.13.
* **Discord library**: `disnake`.
* **Package management**: `uv`.
* **Database**: PostgreSQL via `SQLAlchemy` (asyncio) with `Alembic` migrations.
* **Dependency injection**: `dishka` (defined in `bio_jardas/dependency_injection.py`).
* **Scheduler**: `apscheduler` (async).
* **Observability**: `structlog`.

## Commands

All tasks go through the `Makefile` (includes in `makes/*.mk`). Never invoke `python`, `pip`, `pytest`, `ruff`, or `alembic` directly.

Python:

* `make py/install`: Sync dependencies (`uv lock --check && uv sync --frozen --all-groups`).
* `make py/fmt`: Format and autofix with `ruff`.
* `make py/lint`: Lint and format-check with `ruff`.
* `make py/test`: Run the full test suite (`uv run -m pytest tests/`).
* Run a single test: `uv run -m pytest tests/path/to/test_file.py::test_name`.
* `make py/ipython`: Interactive shell with `.ipython_startup.py` preloaded.

Database:

* `make docker/up`: Start local Postgres via `docker-compose`.
* `make docker/down`: Stop services.
* `make docker/downv`: Stop services and remove volumes.
* `make db/upgrade`: Apply migrations to head (or pass `revision=<rev>`).
* `make db/revision m="description"`: Autogenerate a new Alembic migration.
* `make db/downgrade revision="<rev>"`: Downgrade to a specific revision.

Dependencies:

* `uv add <package>`: Add a runtime dependency.
* `uv add --group <group> <package>`: Add to a specific group (see `dev`, `etl` in `pyproject.toml`).

## Architecture

### Layered DDD per domain

Each domain under `bio_jardas/domains/<name>/` is self-contained and typically contains:

* `models.py`: SQLAlchemy models.
  * Inherit from `Base` (in `bio_jardas/db/models.py`) for standard tables (auto-includes `id`).
  * Inherit from `AuditBase` for tables needing `created_at`, `updated_at`, `created_by`, `updated_by`.
* `repositories.py`: Data access layer.
  * Inherit from `Repository` or `CRUDRepository` (in `bio_jardas/db/repositories.py`).
  * Set `model_type` on `CRUDRepository` subclasses to get `get_by_id`, `add`, `delete`, `get_many`, `exists`, etc.
* `services.py`: Business logic layer.
  * Orchestrates repositories and owns domain rules (scoring, weighted rolls, cooldown decisions, complex interactions).
* `cogs.py` (or `cogs/` package): `disnake` entry points (slash commands, listeners).
  * Inherit from `BaseCog` (in `bio_jardas/cogs.py`).
  * Parse Discord input, call services, send responses or emoji feedback.
* `objects.py`, `dtos.py`, `enums.py`: Value objects, transfer objects, and domain-specific constants.

### Dependency flow

One-way: `Cog -> Service -> Repository -> AsyncSession`. All wiring lives in `bio_jardas/dependency_injection.py`.

### Current domains

* `config`: Global bot settings (e.g., reply intensity).
* `message`: Core reply engine. Handles message groups, weighted rolls for channel and user replies, and dynamic handlers like `caralhamos`. Used by most other domains for response text.
* `game`: Mini-game state: tracking scores and streaks (e.g., Russian Roulette).
* `time_gate`: Cooldowns and timed restrictions (self-bans, per-feature lockouts).
* `schedule`: Background tasks via `apscheduler` (event reminders, periodic messages).

### Key relationships

* `message` and `config`: `MessageService` (via Cogs) checks `ConfigService` for global intensity before replying.
* `schedule` and `message`: Scheduled jobs use `MessageService` to fetch random messages from specific groups for periodic announcements.
* `game` and `time_gate`: Games like roulette interact with `time_gate` to apply temporary "bans" or cooldowns on failure.

### Dependency injection (`dishka`)

* Cog methods that need injected deps: decorate with `@cog_inject` (from `bio_jardas.dependency_injection`); dependencies MUST be keyword-only arguments typed as `FromDishka[DependencyType]`.
* Scheduler jobs: decorate with `@job_inject`, same injection pattern.
* Adding a new dependency requires an `@provide` method on the appropriate `Provider` class in `bio_jardas/dependency_injection.py` (usually `RepositoryProvider` or `ServiceProvider`, both `Scope.REQUEST`).
* `AsyncSession` is provided per-request by `AsyncSessionProvider`, wrapping `bio_jardas.db.engine.transaction()` (commits on success, rolls back on error).

### Cog conventions

* Inherit from `BaseCog` (`bio_jardas/cogs.py`); it exposes `self.bot` and `self.container` (the `dishka` container).
* For `on_message` listeners, wrap the handler with `@skip_bots_and_commands` (from `bio_jardas/decorators.py`) so bot messages and valid bot commands are ignored.
* Use the `emojis` module for consistent user-facing feedback on success and failure.

## Configuration

`bio_jardas/settings.py` uses `pydantic-settings` with nested env vars (delimiter `_`, one split). The `.env` file provides:

* Discord: `DISCORD_TOKEN`.
* Postgres: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DATABASE`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
* Game: `GAME_SHADOW_BAN_ROLE`, `GAME_MEMBER_ROLE`.
* Logging: `LOG_LEVEL`, optional `LOG_FORCE_CONSOLE_RENDERER`.
* Timezone: optional `TIMEZONE` (defaults to `Europe/Lisbon`).

Copy `.env.sample` to `.env` when starting fresh or when the sample is updated.

## Testing

* `pytest` with `pytest-asyncio` in `asyncio_mode = "auto"`. Do NOT add `@pytest.mark.asyncio` to tests or fixtures: the mode handles it automatically.
* **High-fidelity**: never mock the database or swap in a different engine (like SQLite). Always use the project's real PostgreSQL instance from `docker-compose` (`make docker/up`).
* **Isolation**: `tests/conftest.py` provides a session-scoped `_engine` fixture that runs Alembic migrations once, and a per-test `session` fixture that wraps each test in a transaction which rolls back at teardown. Use the `session` fixture to keep the database clean across tests.
* **Execution**: always run tests via `make py/test` or `uv run -m pytest tests/` so module discovery works.
* **Schema integrity**: for models with complex relationships (e.g., cascading deletes, foreign key constraints), always add explicit tests in `tests/db/test_schema_integrity.py` to ensure the database schema behaves as expected.
* **Verification**: back new features with automated tests in `tests/` whenever possible. Manual verification in a development Discord server is still recommended for Cog-level interactions.

## ETL / Data seeding

`etl/load_messages.py` seeds an empty database with message groups and messages from a CSV:

```
uv run --group etl python etl/load_messages.py path/to/messages.csv
```

Uses `cyclopts` and `pandas` (installed via the `etl` group).

## Observability

* Logging is `structlog`. Get a logger with `structlog.stdlib.get_logger()`.
* Bind per-request context with `bind_contextvars(...)` from `structlog.contextvars`.
* Prefer the project helpers (e.g., `bind_command_context_to_logs(context)`, `bind_listener_context_to_logs(context)`) so logs across features share the same metadata shape.

## Development conventions

* **Tooling**: always prefer `uv run` and the project's `Makefile` targets. Never invoke `python`, `pip`, or `alembic` directly. Use `uv add` to manage dependencies.
* **Domain structure**: when adding new features, follow the existing domain pattern in `bio_jardas/domains/<domain_name>/` described above.
* **Standards**: all code must follow PEP8. NEVER use abbreviations for variables or symbols (e.g., use `channel_id` instead of `cid`). Simple abbreviations are fine in list comprehensions (e.g., `score -> s` or `message_group_choice -> mgc`). Avoid meaningless suffixes like `_val` or `_obj`. Run `make py/fmt` and `make py/lint` before submitting changes.
* **Migrations**: always use `make db/revision` for schema changes. Migration files are auto-formatted by a ruff post-write hook configured under `tool.alembic` in `pyproject.toml`.
* **Error handling**: differentiate user-facing errors (which may be ignored or signaled via emoji) from internal errors in logs. Use `structlog` for internal logging and the `emojis` module for user feedback.
* **Ruff**: `pyproject.toml` selects `ALL` lint rules with a curated ignore list. Run `make py/fmt` to autofix, `make py/lint` to verify.
