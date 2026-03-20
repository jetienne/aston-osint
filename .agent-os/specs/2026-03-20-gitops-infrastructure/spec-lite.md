# Spec Summary (Lite)

Deploy SpiderFoot on a Hetzner VPS with a one-time bootstrap script and a GitOps deploy pipeline via GitHub Actions. The server runs SpiderFoot behind nginx with HTTPS and basic auth, auto-restarts via systemd, and updates on every push to main without manual SSH.
