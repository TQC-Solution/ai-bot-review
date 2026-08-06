## What this is

Project Go — an ad serving backend (Go/Gin) that resolves ad unit configs by tag ID, applies targeting/frequency/blocklist rules, and streams events to Kafka. Two binaries share the same module:

- `cmd/api` — the HTTP API server (Gin)
- `cmd/worker` — an Asynq background worker (currently handles URL-blacklist bloom filter rebuilds)

## Commands

```bash
# Install codegen tools once
go install github.com/githubnemo/CompileDaemon@latest
go install github.com/google/wire/cmd/wire@latest

# Local deps
go mod download
cp .env.example .env   # then edit

# Hot-reload dev server (either binary)
./dev.sh api           # or: ./dev.sh worker

# Build both binaries into ./dist
./build.sh

# Regenerate Wire DI after changing a wire.go / provider set
wire ./cmd/api/
wire ./cmd/worker/

# Run directly without hot reload
go run ./cmd/api
go run ./cmd/worker

# Tests (no test files exist yet in this repo — use standard go test when adding them)
go test ./...
go test ./internal/app/api/v4/... -run TestName -v

# Formatting
gofmt -l .
go vet ./...
```

## Dependency injection (Wire)

Every binary wires its dependencies at compile time via `google/wire`:

- `cmd/<app>/wire.go` — the `wireinject`-tagged build list (source of truth for providers)
- `cmd/<app>/wire_gen.go` — generated; **do not hand-edit**, regenerate with `wire ./cmd/<app>/`
- `cmd/<app>/server.go` — the `Server` struct with `Start`/`Stop`/`Run` lifecycle, holding the long-lived clients (Redis, Kafka, Asynq, Mongo) it must close on shutdown
- `cmd/<app>/main.go` — loads config, sets up logger, calls `Initialize<App>()`, runs the server

When adding a new provider (controller/service/validation/repository), add its constructor to `wire.Build(...)` in `wire.go` and regenerate — don't add it directly to `wire_gen.go`.

## API versioning structure

Each API version is a self-contained vertical slice under `internal/app/api/v{N}/`:

```
v{N}/
  binding/     # request/response DTOs for that version
  validation/  # input validation + parsing (query params → typed metadata)
  controller/  # Gin handlers — thin, delegate to service
  service/     # business logic for that version
```

- `v1` — legacy ad unit event tracking (`POST /v1/adUnits/events`)
- `v3` — viewability tracking (`GET /v3/viewAbility/...`)
- `v4` — current ad unit config resolution (`GET /v4/config/adUnitConfig/:tagId`, `.../passback/:tagId`) — this is where most active work happens
- `system` — cross-cutting internal endpoints: health check, URL blacklist bloom-filter rebuild trigger

Routing is layered: `internal/app/api/router/base_router.go` wires global middleware and mounts `RouterV1`/`RouterV3`/`RouterV4` (each in its own `router_v{N}.go`), which register that version's routes onto the shared `gin.Engine`. Add a new version by creating the `v{N}/{binding,validation,controller,service}` slice, a `router_v{N}.go`, wiring its controller/service/validation constructors into `wire.go`, and mounting it in `base_router.go`.

Types shared across versions (not tied to one API surface) live at the top level: `internal/binding/` (core domain DTOs like `AdUnitConfig`, Kafka payloads), `internal/config/constant/`, `internal/service/` (cache, Kafka), `internal/infrastructure/` (Redis/Kafka/Mongo/Asynq clients).

## Worker

`internal/app/worker/` follows the same handler → service → repository layering as the API, but keyed off Asynq task names (`internal/config/constant/asynq.go`) instead of HTTP routes. `internal/app/worker/service.go`'s `Service` registers task handlers on an `asynq.ServeMux` and runs the Asynq server against a Redis Sentinel connection. To add a task: define its name in the asynq constants, add a repository/service method, wire a handler in `internal/app/worker/handler/`, register it in `service.go`'s mux, and add the provider to `cmd/worker/wire.go`.

## Config

`internal/config/config.go` loads env vars via `caarlos0/env` (struct tags, `,required` enforced at startup) plus `.env` autoloading via `godotenv`. Required vars: `ENV`, `APP_NAME`, `HOST`, `LOG_LEVEL`, `LOG_JSON`, `SENTINEL_LIST`, `SENTINEL_NAME`, `KAFKA_BROKERS` — see `.env.example`. Redis is accessed via Sentinel (`SENTINEL_LIST` comma-separated, `SENTINEL_NAME`), not a plain host:port. `Env == "production"` toggles Gin release mode and disables the default request logger (custom middleware logger is always on).

## BACKEND GO

- Flow: router → middleware → controller (bind + validate) → service → repository → MongoDB. Maintain one-way dependencies only.
- Services must only accept context.Context (never \*gin.Context). Controllers are the only layer allowed to interact with Gin.
- Request DTOs must be defined in app/api/binding (using json and binding tags). Bind requests with ShouldBind\*; do not read the raw request body. Custom validators belong in app/api/validations.
- All responses must go through common/api_response. Business errors must use common.NewAPIError(constant.ErrX). Add new error codes to config/constant/error_code.go.
- MongoDB access is restricted to the repository layer. Service interfaces must be defined in the service layer. Use dependency injection with google/wire via constructors. Do not edit wire_gen.go manually—regenerate it by running wire.
- Error handling: return (result, error); check errors immediately; wrap errors with fmt.Errorf("...: %w"); use errors.Is / errors.As for error inspection. Do not use panic for normal control flow (a recovery middleware is already in place).
  context.Context must be the first parameter and propagated throughout the call chain. Goroutines must respect context cancellation to avoid leaks. Protect shared state appropriately, support graceful shutdown, and run tests with -race.
- Background or scheduled jobs must use Asynq (handlers in app/worker/handler, reuse the service layer, ensure idempotency, and configure MaxRetry). For Kafka, define topics and task names in constant/\*, and ensure consumers are idempotent.
