# mors

Calendar subscription server for Metropolitan gym classes. Rust (axum) server with Python scraper.

## Run

```sh
cd server
just run    # or: cargo run
just dev    # auto-reload (requires cargo-watch)
```

## Subscribe

All classes (default filter):
```
http://localhost:3083/calendar.ics
```

Per-class calendars:
```
http://localhost:3083/calendar/yoga.ics
http://localhost:3083/calendar/cross.ics
http://localhost:3083/calendar/pilates.ics
```

### Available class slugs

| Slug | Classes included |
|---|---|
| `yoga` | Yoga |
| `cross` | Cross-HIIT (all variants), Cross-Met |
| `pilates` | Pilates Stretch, Pilates Strong |
| `zumba` | Zumba |
| `bodypump` | Body Pump |
| `cycling` | Cycling, Cycling Virtual |
| `bodycombat` | Body Combat |
| `bodybalance` | Body Balance |
| `gap` | GAP |
| `stretching` | Stretching, Mio-Stretch, Espalda Sana |
| `running` | Skill Running, Running Club |
| `aquagym` | Aquagym, Aquagym 30 |
| `suspension` | Suspension Training |
| `fitness` | Fitness Condition |
| `all` | Everything (no filter) |

### Alerts

By default, calendar events have **no reminders** — your calendar app won't buzz you.

To get reminders, add `?alert=` with the number of minutes. Works on both default and per-class calendars:

```
http://localhost:3083/calendar.ics?alert=25
http://localhost:3083/calendar/yoga.ics?alert=15
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
| `/calendar.ics` | GET | Default filtered calendar (supports `?alert=N`) |
| `/calendar/{slug}.ics` | GET | Per-class calendar (see slug table above) |
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
