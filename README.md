# CCR Glue Service
FastAPI app to proxy Claude (Anthropic) calls and optionally call Cursor API.
- Set secrets in Replit: CLAUDE_API_KEY, CLAUDE_API_URL (optional), CURSOR_API_KEY, CURSOR_API_URL.
- Run command is configured in .replit.
- Endpoints:
  - GET /health
  - POST /ai/claude {prompt, max_tokens, model}
  - POST /cursor/action {action, payload}
