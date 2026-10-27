export const NODE_TYPES = [
  {
    type: 'trigger',
    label: 'Trigger',
    category: 'Ingestion',
    color: 'from-amber-500/20 to-orange-500/10 border-amber-500/40 text-amber-400',
    icon: 'Zap',
    description: 'Initial entrypoint for event, webhook, or scheduled cron.',
    defaultConfig: {
      default_payload: { message: "Sample incoming data payload" }
    }
  },
  {
    type: 'agent_planner',
    label: 'Planner Agent',
    category: 'AI Agents',
    color: 'from-blue-500/20 to-indigo-500/10 border-blue-500/40 text-blue-400',
    icon: 'Brain',
    description: 'Breaks down workflow goals into actionable subtasks and parameters.',
    defaultConfig: {
      goal: "Analyze input requirements and build phased task plan",
      constraints: ["Strict schema validation", "Preserve SLA"]
    }
  },
  {
    type: 'agent_executor',
    label: 'Execution Agent',
    category: 'AI Agents',
    color: 'from-purple-500/20 to-pink-500/10 border-purple-500/40 text-purple-400',
    icon: 'Cpu',
    description: 'Performs semantic reasoning, code execution, or synthesis tasks.',
    defaultConfig: {
      instruction: "Process inputs and generate structured response",
      system_role: "Senior Automation Specialist",
      temperature: 0.5
    }
  },
  {
    type: 'agent_verifier',
    label: 'Verification Agent',
    category: 'AI Agents',
    color: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/40 text-emerald-400',
    icon: 'ShieldCheck',
    description: 'Audits outputs against safety rules and quality assertions.',
    defaultConfig: {
      criteria: ["Output is valid and non-empty", "Adheres to enterprise safety guardrails"],
      minimum_confidence: 0.85
    }
  },
  {
    type: 'condition',
    label: 'Condition Gate',
    category: 'Control Flow',
    color: 'from-cyan-500/20 to-sky-500/10 border-cyan-500/40 text-cyan-400',
    icon: 'GitFork',
    description: 'Branching logic based on comparison expressions.',
    defaultConfig: {
      left_value: "{{steps.node_1.output.urgency}}",
      operator: "==",
      right_value: "High"
    }
  },
  {
    type: 'integration_email',
    label: 'Email Dispatch',
    category: 'Integrations',
    color: 'from-rose-500/20 to-red-500/10 border-rose-500/40 text-rose-400',
    icon: 'Mail',
    description: 'Sends automated emails with dynamic templating.',
    defaultConfig: {
      to_email: "team@example.com",
      subject: "AI Workflow Notification",
      body: "Workflow execution completed."
    }
  },
  {
    type: 'integration_webhook',
    label: 'Webhook Dispatch',
    category: 'Integrations',
    color: 'from-indigo-500/20 to-blue-500/10 border-indigo-500/40 text-indigo-400',
    icon: 'Globe',
    description: 'Calls external HTTP REST endpoints with payloads.',
    defaultConfig: {
      url: "https://api.example.com/webhook",
      method: "POST",
      payload: {}
    }
  },
  {
    type: 'delay',
    label: 'Delay Timer',
    category: 'Control Flow',
    color: 'from-zinc-500/20 to-slate-500/10 border-zinc-500/40 text-zinc-400',
    icon: 'Clock',
    description: 'Pauses execution flow for specified seconds.',
    defaultConfig: {
      seconds: 2
    }
  }
];

export const STATUS_STYLES = {
  COMPLETED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  RUNNING: 'bg-blue-500/10 text-blue-400 border-blue-500/30 animate-pulse',
  PENDING: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  FAILED: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  RETRYING: 'bg-orange-500/10 text-orange-400 border-orange-500/30 animate-bounce',
  SKIPPED: 'bg-slate-700/30 text-slate-400 border-slate-700',
  CANCELLED: 'bg-zinc-800 text-zinc-400 border-zinc-700'
};
