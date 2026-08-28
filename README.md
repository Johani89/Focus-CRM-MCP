# Focus-CRM-MCP

Standalone MCP-style service for an authorized Reynolds FOCUS CRM integration.

## Capabilities
- Daily Work Plan listing and completion
- Complete tasks with `do_not_send=true` by default
- Customer records and notes
- SMS and email actions
- One-day follow-up scheduling by default
- Appointment creation
- Call outcome logging
- Automatic one-time reauthentication on 401/403

## Railway
Deploy from this repository. The Dockerfile starts FastAPI on Railway's `$PORT`; `/health` is the health check.

Set the FOCUS variables shown in `.env.example` in Railway. Do not commit credentials.

## Important integration note
The endpoint paths in `.env.example` are configurable adapter paths, not a claim that Reynolds exposes those exact public routes. Set `FOCUS_BASE_URL`, login method/fields, and endpoint paths to the authorized interface actually provided by Reynolds/RCI or observed in your authorized FOCUS environment. Do not bypass authentication or security controls.

## MCP endpoints
- `GET /.well-known/mcp.json`
- `GET /sse/`
- `POST /call_tool/`
- `GET /health`
