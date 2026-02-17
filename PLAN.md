# Calendars — Rust Rewrite

Always-running server and dashboard. Starts with gym calendar + scrapers, expandable to other data sources.

## Architecture

```
server/
  Cargo.toml
  justfile
  src/
    main.rs               # axum server, startup, background scheduling
    config.rs             # env vars, class filters, display names, slug mappings
    state.rs              # shared AppState
    routes/
      mod.rs
      calendar.rs         # GET /calendar.ics, GET /calendar/:slug.ics
      dashboard.rs        # GET / — maud HTML (stub)
      health.rs           # GET /health
      refresh.rs          # POST /refresh
    ical.rs               # read/write/merge .ics, filter future, add alarms
```

**Planned (not yet implemented):**
```
    scraper/
      mod.rs              # orchestrator: startup + periodic fetch
      auth.rs             # chromiumoxide login, cookie save/load
      extract.rs          # navigate pages, JS eval, parse GymClass
```

## Stack

| Concern | Choice |
|---------|--------|
| Web framework | axum 0.8 |
| Async runtime | tokio |
| Scraper | Python/Playwright (Rust rewrite planned — see Phase 3) |
| iCal | icalendar crate |
| HTTP client | reqwest |
| Templating | maud 0.27 (not yet used) |
| Config | dotenvy + std::env |
| Errors | anyhow |
| Logging | tracing |
| Task runner | just + cargo-watch |

## Phases

### Phase 1: Scaffold + serve calendar from disk ✅
- Axum server on port 3083
- Read existing `ics_files/*.ics`, merge, filter future events, dedup, serve
- `?alert=N` query param adds VALARM
- `/health` endpoint
- justfile with `dev` (cargo-watch), `build`, `check`

### Phase 2: Per-class subscriptions + dashboard
- `GET /calendar/:slug.ics` — per-class calendar subscriptions (yoga, cross, pilates, etc.)
- `GET /` — maud-rendered HTML dashboard (stub, returns 204)
- Server uptime, last fetch time, event count, subscribe link

### Phase 3: Gym scraper in Rust (not started)
- chromiumoxide headless Chrome
- Cookie persistence to `data/metropolitan_cookies.json`
- Login to Metropolitan, navigate schedule, evaluate EXTRACT_JS
- Filter classes by name, generate .ics
- Background task on startup + POST /refresh + periodic (4h interval)

### Phase 4: Production & cleanup (not started)
- Graceful shutdown
- Process management config
- Archive/remove Python code

## Notes

- chromiumoxide needs Chrome/Chromium installed (`brew install --cask chromium` if needed)
- EXTRACT_JS snippet reused verbatim from Python — evaluated in-browser
- Cookie format will differ from Playwright's — first run needs fresh login
- Scraper is currently Python/Playwright; Rust server shells out to it via `/refresh`
