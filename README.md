# mors

Calendar subscription server for Metropolitan gym classes. Scrapes the class schedule, converts to iCal, and serves it over HTTP.

```
uv run main.py
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

This adds a 25-minute reminder before each class. Use whatever number you want.

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

Full mapping in `gym_calendar/config.py`.

## Other endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Server status, cookie validity, file counts |
| `/refresh` | POST | Trigger a manual data refresh |
| `/check` | GET | Test connection to gym website |

## Config

Credentials in `.env`:

```sh
METROPOLITAN_USER=
METROPOLITAN_PASS=
```

Class filters in `gym_calendar/config.py` — controls which classes appear in the calendar.
