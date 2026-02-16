# Cloudflare Tunnel Setup

Expose your gym calendar via Cloudflare Tunnel for secure HTTPS access from anywhere.

## Quick Setup

### 1. Login to Cloudflare

```bash
cloudflared tunnel login
```

This opens a browser to authenticate with your Cloudflare account.

### 2. Create a Tunnel

```bash
cloudflared tunnel create gymcal
```

This creates a tunnel and saves credentials to `~/.cloudflared/`

### 3. Create Configuration File

touch '~/.cloudflared/config.yml':

```yaml
tunnel: gym-calendar
credentials-file: /Users/m/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: gym.yourdomain.com
    service: http://localhost:3083
  - service: http_status:404
```

Replace:
- `<TUNNEL-ID>` with the ID from step 2
- `gym.yourdomain.com` with your desired subdomain

### 4. Create DNS Record

```bash
cloudflared tunnel route dns gym-calendar gym.yourdomain.com
```

### 5. Start the Tunnel

```bash
cloudflared tunnel run gym-calendar
```

Your calendar is now available at: `https://gym.yourdomain.com/calendar.ics`

## Run as Background Service

### Option 1: Quick Background Process

```bash
nohup cloudflared tunnel run gym-calendar > /tmp/cloudflared.log 2>&1 &
```

### Option 2: Install as Service (Recommended)

```bash
sudo cloudflared service install
sudo launchctl start com.cloudflare.cloudflared
```

This runs automatically on boot.

## Alternative: Quick Tunnel (No Domain Required)

For testing or temporary use:

```bash
cloudflared tunnel --url http://localhost:3083
```

This gives you a temporary URL like: `https://random-words.trycloudflare.com`

⚠️ **Note**: This URL changes each time and is temporary.

## Configuration

### Custom Port

If your server runs on a different port:

```yaml
ingress:
  - hostname: gym.yourdomain.com
    service: http://localhost:3000  # Change port here
  - service: http_status:404
```

### Multiple Routes

Serve multiple endpoints:

```yaml
ingress:
  - hostname: gym.yourdomain.com
    service: http://localhost:3083
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

## Useful Commands

### Check Tunnel Status
```bash
cloudflared tunnel info gym-calendar
cloudflared tunnel list
```

### View Logs
```bash
# If running as service
tail -f /tmp/cloudflared.log

# Or system logs
sudo launchctl list | grep cloudflare
```

### Stop Service
```bash
sudo launchctl stop com.cloudflare.cloudflared
```

### Uninstall Service
```bash
sudo cloudflared service uninstall
```

### Delete Tunnel
```bash
cloudflared tunnel delete gym-calendar
```

## Endpoints

Once your tunnel is running, these endpoints are available:

- `https://gym.yourdomain.com/calendar.ics` - Calendar feed
- `https://gym.yourdomain.com/health` - Health check
- `https://gym.yourdomain.com/refresh` - Manual refresh (POST)

## Security Benefits

- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **No Port Forwarding**: Works behind any firewall/NAT
- ✅ **DDoS Protection**: Cloudflare's network protection
- ✅ **Access Control**: Use Cloudflare Access for authentication
- ✅ **Global CDN**: Fast access worldwide

## Troubleshooting

### "Unable to reach origin service"

Check if the local server is running:
```bash
curl http://localhost:3083/health
```

If not running, start it:
```bash
launchctl start com.user.gymcalendar
```

### Check Tunnel Connection

```bash
cloudflared tunnel info gym-calendar
```

Should show status as "healthy"

### Test Local Connection First

```bash
# Test local server
curl http://localhost:3083/calendar.ics

# Test tunnel
curl https://gym.yourdomain.com/calendar.ics
```

### View Tunnel Logs

```bash
cloudflared tunnel run gym-calendar
```

Look for connection errors or SSL issues.

## Cloudflare Access (Optional)

Add authentication to your calendar:

1. Go to Cloudflare Dashboard → Zero Trust → Access
2. Create an Application:
   - Name: Gym Calendar
   - Domain: `gym.yourdomain.com`
3. Add Policy:
   - Rule: Email domain is `yourdomain.com`
   - Or: Specific email addresses

Now only authorized users can access your calendar.

## Comparison: Cloudflare vs Tailscale

| Feature | Cloudflare Tunnel | Tailscale Serve |
|---------|------------------|-----------------|
| Public Access | ✅ Yes | ❌ Only your tailnet |
| Custom Domain | ✅ Yes | ❌ No |
| DDoS Protection | ✅ Yes | ✅ Yes |
| Setup Complexity | Medium | Easy |
| Cost | Free tier available | Free |
| Speed | Via CDN | Direct P2P |
| Privacy | Through Cloudflare | End-to-end encrypted |

**Recommendation**: 
- Use Cloudflare if you need a custom domain or public access
- Use Tailscale for private, personal use only

## Complete Example

```bash
# 1. Login
cloudflared tunnel login

# 2. Create tunnel
cloudflared tunnel create gym-calendar
# Note the tunnel ID from output

# 3. Create config
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: gym-calendar
credentials-file: /Users/m/.cloudflared/YOUR-TUNNEL-ID.json

ingress:
  - hostname: gym.yourdomain.com
    service: http://localhost:3083
  - service: http_status:404
EOF

# 4. Create DNS
cloudflared tunnel route dns gym-calendar gym.yourdomain.com

# 5. Install as service
sudo cloudflared --config ~/.cloudflared/config.yml service install
sudo launchctl start com.cloudflare.cloudflared

# 6. Test
curl https://gym.yourdomain.com/health
```

Done! Your calendar is now accessible via HTTPS. 🎉
