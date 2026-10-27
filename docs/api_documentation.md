# REST API Documentation

The AI Workflow Automation System exposes a RESTful API versioned under `/api/v1`.

## Authentication
Pass your API key in the `X-API-KEY` header:
```http
X-API-KEY: ai-wf-key-default-admin-2026
```

---

## 1. System & Metrics Endpoints

### Health Check
- **Endpoint**: `GET /health`
- **Response**:
```json
{
  "status": "healthy",
  "service": "AI Workflow Automation System",
  "version": "1.0.0",
  "mock_llm_mode": true
}
```

### Dashboard Statistics
- **Endpoint**: `GET /api/v1/stats`
- **Response**:
```json
{
  "total_workflows": 3,
  "active_workflows": 3,
  "total_executions": 12,
  "completed_executions": 12,
  "failed_executions": 0,
  "running_executions": 0,
  "success_rate_percent": 100.0,
  "average_duration_seconds": 0.42
}
```

---

## 2. Workflows API (`/api/v1/workflows`)

### List Workflows
- **Endpoint**: `GET /api/v1/workflows?skip=0&limit=50&status=active`
- **Response**: Array of `WorkflowResponse` objects.

### Create Workflow
- **Endpoint**: `POST /api/v1/workflows`
- **Request Body**:
```json
{
  "name": "Custom Triage Pipeline",
  "description": "Multi-agent customer email responder",
  "status": "active",
  "trigger_type": "manual",
  "nodes": [
    {
      "id": "node_1",
      "type": "trigger",
      "name": "Trigger",
      "config": {},
      "position": { "x": 100, "y": 150 }
    }
  ],
  "edges": []
}
```

### Get Workflow by ID
- **Endpoint**: `GET /api/v1/workflows/{workflow_id}`

### Update Workflow
- **Endpoint**: `PUT /api/v1/workflows/{workflow_id}`

### Delete Workflow
- **Endpoint**: `DELETE /api/v1/workflows/{workflow_id}`
- **Response**: `204 No Content`

### Trigger Workflow Execution
- **Endpoint**: `POST /api/v1/workflows/{workflow_id}/execute`
- **Request Body**:
```json
{
  "trigger_payload": {
    "customer_id": "cust_12345",
    "inquiry": "Need urgent API rate limit increase"
  },
  "run_async": false
}
```

### Import Workflow Template
- **Endpoint**: `POST /api/v1/workflows/import`
- **Request Body**: Full workflow JSON definition.

### Export Workflow
- **Endpoint**: `GET /api/v1/workflows/{workflow_id}/export`

---

## 3. Executions API (`/api/v1/executions`)

### List Executions
- **Endpoint**: `GET /api/v1/executions?workflow_id={id}&status={status}&limit=50`

### Get Execution Run Details
- **Endpoint**: `GET /api/v1/executions/{execution_id}`
- **Response**: Includes `step_executions` breakdown and `result`.

### Get Chronological Execution Logs
- **Endpoint**: `GET /api/v1/executions/{execution_id}/logs`

### Cancel Running Execution
- **Endpoint**: `POST /api/v1/executions/{execution_id}/cancel`

### Retry Failed Execution
- **Endpoint**: `POST /api/v1/executions/{execution_id}/retry`

---

## 4. Integrations API (`/api/v1/integrations`)

### Test Email
- **Endpoint**: `POST /api/v1/integrations/test-email`
- **Request Body**:
```json
{
  "to_email": "ops@company.internal",
  "subject": "System Verification Alert",
  "body": "All workflow units operating nominally."
}
```

### Inspect Outbox
- **Endpoint**: `GET /api/v1/integrations/email-outbox?limit=50`

### Test Outbound Webhook
- **Endpoint**: `POST /api/v1/integrations/test-webhook`
- **Request Body**:
```json
{
  "url": "https://api.example.com/test",
  "method": "POST",
  "payload": { "ping": "pong" }
}
```

### Test LLM Agent Generation
- **Endpoint**: `POST /api/v1/integrations/test-llm`
- **Request Body**:
```json
{
  "prompt": "Evaluate support inquiry response for SLA compliance.",
  "provider": "mock"
}
```
