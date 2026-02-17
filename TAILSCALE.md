# Tailscale Serve Setup

This guide explains how to expose your gym calendar via Tailscale Serve for secure access from anywhere on your tailnet.

## Quick Setup

### 1. Start the Calendar Server

```bash
cd /Users/m/dev/mors/server
just run    # or: cargo run
```

### 2. Enable Tailscale Serve

In another terminal:

```bash
tailscale serve --bg http://localhost:3083
```

This creates an HTTPS endpoint at: `https://<your-machine>.ts.net/`

### 3. Subscribe to Calendar

Your calendar will be available at:
```
https://<your-machine>.ts.net/calendar.ics
```

Replace `<your-machine>` with your Tailscale machine name.

## Useful Commands

### Check Current Configuration
```bash
tailscale serve status
```

### Stop Serving
```bash
tailscale serve reset
```

### Serve on a Specific Port
```bash
PORT=3000 cargo run

tailscale serve https / http://localhost:3000
```

## Endpoints

Once served via Tailscale, these endpoints are available:

- `https://<machine>.ts.net/calendar.ics` - Calendar feed
- `https://<machine>.ts.net/calendar/<class>.ics` - Per-class calendar feed
- `https://<machine>.ts.net/health` - Health check
- `https://<machine>.ts.net/refresh` - Manual refresh (POST)

## Production Recommendations

### 1. Use a Process Manager

Instead of running manually, use a process manager to keep the server running:

**Using `launchd` (macOS):**

Create `~/Library/LaunchAgents/com.user.mors.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.mors</string>
    <key>ProgramArguments</key>
    <array>
        <string>cargo</string>
        <string>run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/m/dev/mors/server</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/mors.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mors.err</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.user.mors.plist
launchctl start com.user.mors
```

### 2. Set Up Tailscale Serve to Start on Boot

Tailscale Serve configuration persists across reboots automatically.

### 3. Monitor Health

```bash
curl https://<machine>.ts.net/health

tail -f /tmp/mors.log
```

## Troubleshooting

### "No calendar data available"

The server needs .ics files in `ics_files/`. Trigger a scrape:
```bash
curl -X POST https://<machine>.ts.net/refresh
```

### Check Server Status
```bash
curl http://localhost:3083/health

tailscale serve status
```

### Reset and Restart
```bash
tailscale serve reset

# Kill server (find the cargo/mors process)
pkill -f mors

# Restart
cd /Users/m/dev/mors/server
nohup cargo run > /tmp/mors.log 2>&1 &

tailscale serve https / http://localhost:3083
```

## Security Notes

- Calendar data is only accessible on your tailnet (private network)
- HTTPS is automatically enabled by Tailscale
- No public internet exposure
- Use Tailscale ACLs to restrict access if needed
- Credentials are stored locally in `.env` (never transmitted)
- Cookies stored in `data/` directory (gitignored)

## Alternative: Tailscale Funnel

If you want to share with people NOT on your tailnet:

```bash
tailscale funnel 3083
```

Warning: This makes your calendar PUBLIC on the internet.
