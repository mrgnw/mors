# Tailscale Serve Setup

This guide explains how to expose your gym calendar via Tailscale Serve for secure access from anywhere on your tailnet.

## Quick Setup

### 1. Start the Calendar Server

```bash
# Starts on port 3083 by default
cd /Users/m/dev/calendars
uv run main.py
```

### 2. Enable Tailscale Serve

In another terminal:

```bash
# Serve port 3083 over HTTPS on your tailnet
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
# If you want to use a different port locally
PORT=3000 uv run main.py

# Then serve that port
tailscale serve https / http://localhost:3000
```

## Benefits

- ✅ **Secure**: HTTPS with automatic certificate management
- ✅ **Private**: Only accessible on your tailnet
- ✅ **No Port Forwarding**: Works behind NAT/firewalls
- ✅ **Mobile Access**: Access from phone, tablet, etc.
- ✅ **Multiple Devices**: Subscribe on all your devices

## Endpoints

Once served via Tailscale, these endpoints are available:

- `https://<machine>.ts.net/calendar.ics` - Calendar feed
- `https://<machine>.ts.net/health` - Health check
- `https://<machine>.ts.net/refresh` - Manual refresh (POST)

## Production Recommendations

### 1. Use a Process Manager

Instead of running manually, use a process manager to keep the server running:

**Using `launchd` (macOS):**

Create `~/Library/LaunchAgents/com.user.gymcalendar.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.gymcalendar</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/uv</string>
        <string>run</string>
        <string>main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/m/dev/calendars</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/gymcalendar.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/gymcalendar.err</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.user.gymcalendar.plist
launchctl start com.user.gymcalendar
```

### 2. Set Up Tailscale Serve to Start on Boot

Tailscale Serve configuration persists across reboots automatically.

### 3. Monitor Health

```bash
# Check if server is running
curl https://<machine>.ts.net/health

# Check logs
tail -f /tmp/gymcalendar.log
```

## Troubleshooting

### "No calendar data available"

The server needs time to fetch data on first start. Wait 10-15 seconds, then try again.

Or manually trigger refresh:
```bash
curl -X POST https://<machine>.ts.net/refresh
```

### Check Server Status
```bash
# Is the local server running?
curl http://localhost:3083/health

# Is Tailscale Serve configured?
tailscale serve status
```

### Reset and Restart
```bash
# Stop Tailscale Serve
tailscale serve reset

# Kill server
pkill -f main.py

# Restart server
cd /Users/m/dev/calendars
nohup uv run main.py > /tmp/gymcalendar.log 2>&1 &

# Re-enable Tailscale Serve
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

⚠️ **Warning**: This makes your calendar PUBLIC on the internet. Only use if you want to share with others outside your tailnet.
