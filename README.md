# AI Workflow Automation System

An enterprise-grade, autonomous multi-agent orchestration and workflow automation platform. Designed for high-reliability systems, this platform features visual DAG pipeline creation, deterministic topological scheduling, real-time agent thought auditing, and self-healing automated retry loops with exponential backoff.

![AI Workflow Automation System](https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/workflow.svg)

---

## 🌟 Key Features

- **Autonomous Multi-Agent Architecture**:
  - **Planner Agent**: Decomposes high-level objectives into phased subtasks and parameter contracts.
  - **Execution Agent**: Synthesizes responses, executes code, generates structured JSON, and integrates cognitive reasoning.
  - **Verification Agent**: Acts as an automated quality gate and safety guardrail, inspecting confidence thresholds and schema compliance.
- **Resilient DAG Execution Engine**:
  - **Kahn's Algorithm Cycle Detection**: Validates all graph connections before run initiation.
  - **Dynamic Variable Interpolation**: Downstream nodes reference upstream step outputs using `{{steps.<node_id>.output.<field>}}` or environment values `{{env.KEY}}`.
  - **Conditional Branching**: Evaluates comparison expressions (`==`, `!=`, `>`, `<`, `contains`) and dynamically triggers target paths while marking unselected paths as `SKIPPED`.
  - **Exponential Backoff with Jitter**: Automatically retries transient network or verification faults up to configured thresholds.
- **Enterprise Integrations**:
  - **Email Connector**: Full SMTP support with live delivery or simulated outbox inspection.
  - **Webhook Connector**: Outbound and inbound HTTP calls with signature verification and header customization.
  - **Unified LLM Adapter**: Supports Google Gemini, OpenAI, and a built-in zero-dependency simulated offline agent engine.
- **Modern Interactive Frontend**:
  - Visual drag-and-drop workflow canvas with customizable nodes.
  - Real-time execution status tracking and chronological log viewer with `AGENT_THOUGHT` traces.
  - Live pipeline metrics dashboard.

---

## 📂 Repository Structure

```
ai-workflow-automation-system/
│
├── frontend/
│   ├── public/
│   │   └── logo.svg
│   └── src/
│       ├── components/
│       │   ├── WorkflowBuilder.jsx     # Visual DAG canvas builder
│       │   ├── WorkflowNode.jsx        # Custom node renderer with ports & state
│       │   ├── ExecutionHistory.jsx    # Table of past runs with status badges
│       │   ├── ExecutionLogs.jsx       # Real-time console for agent thoughts & traces
│       │   └── Navbar.jsx              # Navigation header with health check
│       ├── pages/
│       │   ├── Dashboard.jsx           # High-level metrics, active runs, quick launch
│       │   ├── Workflows.jsx           # Searchable workflow list, import/export
│       │   ├── CreateWorkflow.jsx      # Canvas studio with template presets
│       │   └── WorkflowDetails.jsx     # Node inspector, trigger modal, execution details
│       ├── services/
│       │   └── api.js                  # Axios client for FastAPI endpoints
│       ├── hooks/
│       ├── utils/
│       │   ├── constants.js            # Node types, colors, icons, status mappings
│       │   └── formatters.js           # Timestamp & latency formatters
│       ├── App.jsx                     # Top-level SPA router & state
│       ├── main.jsx                    # React 18 DOM root
│       └── index.css                   # Tailwind base & custom styles
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & startup lifecycle
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic BaseSettings & environment configs
│   │   │   ├── security.py             # API Key verification & auth helpers
│   │   │   └── logging_config.py       # Formatted logger for execution tracing
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── workflows.py        # CRUD, DAG validation, import/export
│   │   │       ├── executions.py       # Trigger, inspect, cancel, retry runs
│   │   │       └── integrations.py     # Email, webhook, LLM test endpoints
│   │   ├── models/
│   │   │   ├── workflow.py             # SQLAlchemy models for Workflow & Schedules
│   │   │   ├── execution.py            # Executions, StepExecutions, ExecutionLogs
│   │   │   └── user.py                 # Users & API credentials
│   │   ├── schemas/
│   │   │   ├── workflow.py             # Pydantic schemas for DAG contracts
│   │   │   └── execution.py            # Execution and log schemas
│   │   ├── services/
│   │   │   ├── workflow_service.py     # Business logic for workflows
│   │   │   ├── execution_service.py    # Run lifecycle & background worker dispatch
│   │   │   └── notification_service.py # System alerts & email dispatches
│   │   ├── engine/
│   │   │   ├── workflow_engine.py      # Asynchronous DAG orchestrator
│   │   │   ├── task_executor.py        # Dispatches nodes by type
│   │   │   ├── dependency_resolver.py  # Topological sorting & interpolation
│   │   │   └── retry_handler.py        # Backoff calculation & retry policies
│   │   ├── agents/
│   │   │   ├── planner_agent.py        # Task decomposition agent
│   │   │   ├── execution_agent.py      # Cognitive reasoning agent
│   │   │   └── verification_agent.py   # Guardrails & quality auditor
│   │   ├── integrations/
│   │   │   ├── email_integration.py    # SMTP email connector & outbox
│   │   │   ├── webhook_integration.py  # HTTP webhook dispatcher
│   │   │   └── llm_integration.py      # Gemini/OpenAI adapter & mock fallback
│   │   ├── db/
│   │   │   ├── database.py             # SQLAlchemy session & Base
│   │   │   └── migrations/
│   │   ├── workers/
│   │   │   └── workflow_worker.py      # Independent background execution worker
│   │   └── tests/
│   │       ├── test_workflows.py       # API CRUD and cycle detection tests
│   │       ├── test_engine.py          # DAG execution & interpolation tests
│   │       └── test_integrations.py    # Email, webhook, LLM integration tests
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
│
├── workflows/
│   ├── email_automation.json           # Template: Support email triage & reply
│   ├── report_generation.json          # Template: Scheduled KPI analytics digest
│   └── customer_support.json           # Template: Multi-tier escalation with condition
│
├── infrastructure/
│   ├── docker-compose.yml              # Multi-container service composition
│   └── deployment/
│       ├── k8s-deployment.yaml         # Kubernetes Deployment & Service specs
│       └── nginx.conf                  # Nginx reverse proxy configuration
│
├── docs/
│   ├── architecture.md                 # System architecture & Mermaid flowcharts
│   ├── api_documentation.md            # Complete REST endpoints reference
│   └── setup_guide.md                  # Local dev & production deployment instructions
│
├── .env.example                        # Template environment variables
├── .gitignore                          # Git ignore definitions
├── README.md                           # Project documentation
└── LICENSE                             # MIT License
```

---

## 🚀 Quick Start

### 1. Run with Docker Compose
```bash
cd infrastructure
docker-compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`

### 2. Run Locally

#### Backend:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Running Automated Tests

The backend test suite covers DAG validation, cycle detection, exponential backoff, LLM integrations, email outbox, and full end-to-end workflow execution:

```bash
cd backend
python -m pytest app/tests -v
```

All 10 test suites pass out of the box with zero external dependencies required.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
