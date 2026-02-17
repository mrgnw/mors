# Calendars — Rust Rewrite

Always-running server and dashboard. Starts with gym calendar + scrapers, expandable to other data sources.

## Architecture

```
server/
  Cargo.toml
  justfile
  src/
    main.rs               # axum server, startup, background scheduling
    config.rs             # env vars, class filters, display names
    state.rs              # shared AppState
    routes/
      mod.rs
      calendar.rs         # GET /calendar.ics (?alert=N)
      dashboard.rs        # GET / — maud HTML
      health.rs           # GET /health
      refresh.rs          # POST /refresh
    scraper/
      mod.rs              # orchestrator: startup + periodic fetch
      auth.rs             # chromiumoxide login, cookie save/load
      extract.rs          # navigate pages, JS eval, parse GymClass
    ical.rs               # read/write/merge .ics, filter future, add alarms
    claude_usage.rs       # Anthropic Claude Code analytics API
```

## Stack

| Concern | Choice |
|---------|--------|
| Web framework | axum 0.8 |
| Async runtime | tokio |
| Scraper | chromiumoxide (CDP) |
| iCal | icalendar crate |
| HTTP client | reqwest |
| Templating | maud 0.27 |
| Config | dotenvy + std::env |
| Errors | anyhow |
| Logging | tracing |
| Task runner | just + cargo-watch |

## Phases

### Phase 1: Scaffold + serve calendar from disk
- Axum server on port 3083
- Read existing `ics_files/*.ics`, merge, filter future events, dedup, serve
- `?alert=N` query param adds VALARM
- `/health` endpoint
- justfile with `dev` (cargo-watch), `build`, `check`

### Phase 2: Dashboard + Claude Code usage
- `GET /` — maud-rendered HTML dashboard
- Server uptime, last fetch time, event count, subscribe link
- Claude Code analytics via Admin API (`/v1/organizations/usage_report/claude_code`)
- Needs `ANTHROPIC_ADMIN_KEY` (sk-ant-admin...) in .env

### Phase 3: Gym scraper in Rust
- chromiumoxide headless Chrome
- Cookie persistence to `data/metropolitan_cookies.json`
- Login to Metropolitan, navigate schedule, evaluate EXTRACT_JS
- Filter classes by name, generate .ics
- Background task on startup + POST /refresh + periodic (4h interval)

### Phase 4: Production & cleanup
- Graceful shutdown
- ubermind process management config
- Archive/remove Python code

## Notes

- chromiumoxide needs Chrome/Chromium installed (`brew install --cask chromium` if needed)
- EXTRACT_JS snippet reused verbatim from Python — evaluated in-browser
- Cookie format will differ from Playwright's — first run needs fresh login
- Admin API key required for Claude Code analytics (Console > Settings > Admin Keys)
