# mors

Calendar subscription server for Metropolitan gym classes. Rust (axum) server with Python scraper.

## Run

```sh
cd server
just run    # or: cargo run
just dev    # auto-reload (requires cargo-watch)
```

## Subscribe

```
http://localhost:3083/calendar.ics
```

### Alerts

By default, calendar events have **no reminders** — your calendar app won't buzz you.

To get reminders, add `?alert=` with the number of minutes:

```
http://localhost:3083/calendar.ics?alert=25
```

### Class names

Classes show up with readable names and emoji instead of the gym's raw ALL-CAPS names:

| Calendar shows | Instead of |
|---|---|
| 🏋️ Body Pump | BODY PUMP |
| 💥 Cross-HIIT Challenge | CROSS-HIIT CHALLENGE |
| 🧘 Yoga | YOGA |
| 🪩 Zumba | ZUMBA |
| 🍑 GAP | GAP |
| 🔥 Fitness Condition | FITNESS CONDITION |
| 🌀 Pilates Stretch | PILATES-STRETCH |
| 💪 Pilates Strong | PILATES-STRONG |
| ⚡ Suspension Training | SUSPENSION TRAINING |
| 🏃 Skill Running | SKILL RUNNING |

Full mapping in `server/src/config.rs`.

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/calendar.ics` | GET | Merged calendar (supports `?alert=N`) |
| `/health` | GET | Server status, file counts, last fetch |
| `/refresh` | POST | Trigger a manual data refresh |

## Config

Credentials in `.env`:

```sh
METROPOLITAN_USER=
METROPOLITAN_PASS=
```

Class filters and display names in `server/src/config.rs`.

## Scraper

The scraper (`fetch_gym_data.py`) is still Python/Playwright. The Rust server calls it via `/refresh`. To run manually:

```sh
uv run python fetch_gym_data.py
```
