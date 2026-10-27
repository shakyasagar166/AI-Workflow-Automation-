import React, { useState } from 'react';
import { Save, ArrowLeft, Sparkles, Layers, CheckCircle2 } from 'lucide-react';
import WorkflowBuilder from '../components/WorkflowBuilder';
import { createWorkflow, executeWorkflow } from '../services/api';

const PRESET_TEMPLATES = {
  blank: {
    name: 'New Custom Autonomous Pipeline',
    description: 'Custom multi-agent DAG pipeline configured from scratch',
    trigger_type: 'manual',
    nodes: [
      {
        id: 'node_init_trigger',
        type: 'trigger',
        name: 'Manual Trigger',
        config: { default_payload: { task: 'Sample input data' } },
        position: { x: 80, y: 150 },
      },
    ],
    edges: [],
  },
  email_triage: {
    name: 'Autonomous Support Email Triage',
    description: 'Ingests customer emails, analyzes sentiment & urgency, crafts verified resolution, and replies.',
    trigger_type: 'webhook',
    nodes: [
      {
        id: 'trig_email',
        type: 'trigger',
        name: 'Email Webhook Trigger',
        config: {
          default_payload: {
            from_email: 'alex@startup.io',
            subject: 'Billing question about team seat charges',
            body: 'Hi, we were charged for 5 seats instead of 3. Can you check our subscription invoice?'
          }
        },
        position: { x: 60, y: 150 },
      },
      {
        id: 'agent_plan',
        type: 'agent_planner',
        name: 'Triage Planner Agent',
        config: { goal: 'Categorize query and plan customer support resolution strategy' },
        position: { x: 340, y: 150 },
      },
      {
        id: 'agent_exec',
        type: 'agent_executor',
        name: 'Response Drafting Agent',
        config: {
          instruction: 'Draft an empathetic, helpful response clarifying the billing invoice adjustment.',
          system_role: 'Senior Customer Success Lead'
        },
        position: { x: 620, y: 150 },
      },
      {
        id: 'agent_verif',
        type: 'agent_verifier',
        name: 'Verification Guardrail',
        config: {
          criteria: ['Polite tone', 'No unverified transaction numbers', 'Accurate billing guidance'],
          minimum_confidence: 0.85
        },
        position: { x: 900, y: 150 },
      },
      {
        id: 'email_out',
        type: 'integration_email',
        name: 'Send Customer Reply',
        config: {
          to_email: '{{steps.trig_email.output.payload.from_email}}',
          subject: 'Re: {{steps.trig_email.output.payload.subject}}',
          body: '{{steps.agent_exec.output.output.response_draft}}'
        },
        position: { x: 1180, y: 150 },
      }
    ],
    edges: [
      { id: 'e1', source: 'trig_email', target: 'agent_plan' },
      { id: 'e2', source: 'agent_plan', target: 'agent_exec' },
      { id: 'e3', source: 'agent_exec', target: 'agent_verif' },
      { id: 'e4', source: 'agent_verif', target: 'email_out' },
    ]
  },
  kpi_digest: {
    name: 'Executive Telemetry & KPI Digest',
    description: 'Aggregates platform telemetry, drafts executive analytical briefing, checks accuracy, and notifies.',
    trigger_type: 'schedule',
    nodes: [
      {
        id: 'cron_trig',
        type: 'trigger',
        name: 'Daily Schedule Trigger',
        config: { default_payload: { window: 'past_24_hours', cluster: 'production-primary' } },
        position: { x: 80, y: 150 },
      },
      {
        id: 'exec_agent_kpi',
        type: 'agent_executor',
        name: 'Analytics Synthesis Agent',
        config: { instruction: 'Compile throughput and latency KPI audit report with recommendations.' },
        position: { x: 380, y: 150 },
      },
      {
        id: 'verif_agent_kpi',
        type: 'agent_verifier',
        name: 'Report Verifier Guardrail',
        config: { criteria: ['Valid structured metrics', 'Clear takeaways'], minimum_confidence: 0.9 },
        position: { x: 680, y: 150 },
      },
      {
        id: 'webhook_dispatch',
        type: 'integration_webhook',
        name: 'Notify Webhook',
        config: { url: 'https://api.example.com/webhook/kpi', method: 'POST' },
        position: { x: 980, y: 150 },
      }
    ],
    edges: [
      { id: 'ek1', source: 'cron_trig', target: 'exec_agent_kpi' },
      { id: 'ek2', source: 'exec_agent_kpi', target: 'verif_agent_kpi' },
      { id: 'ek3', source: 'verif_agent_kpi', target: 'webhook_dispatch' },
    ]
  }
};

export default function CreateWorkflow({ onNavigate, onSelectWorkflow, onSelectExecution }) {
  const [name, setName] = useState('New Autonomous Pipeline');
  const [description, setDescription] = useState('Multi-agent workflow orchestration');
  const [triggerType, setTriggerType] = useState('manual');
  const [nodes, setNodes] = useState(PRESET_TEMPLATES.blank.nodes);
  const [edges, setEdges] = useState(PRESET_TEMPLATES.blank.edges);
  const [isSaving, setIsSaving] = useState(false);

  const handleSelectTemplate = (templateKey) => {
    const tmpl = PRESET_TEMPLATES[templateKey];
    if (!tmpl) return;
    setName(tmpl.name);
    setDescription(tmpl.description);
    setTriggerType(tmpl.trigger_type);
    setNodes(JSON.parse(JSON.stringify(tmpl.nodes)));
    setEdges(JSON.parse(JSON.stringify(tmpl.edges)));
  };

  const handleSave = async () => {
    if (!name.trim()) {
      alert('Please enter a workflow name.');
      return;
    }
    setIsSaving(true);
    try {
      const created = await createWorkflow({
        name,
        description,
        status: 'active',
        trigger_type: triggerType,
        nodes,
        edges,
      });
      alert('Workflow created successfully!');
      if (onSelectWorkflow) onSelectWorkflow(created.id);
      else onNavigate('workflows');
    } catch (err) {
      alert('Failed to save workflow: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveAndExecute = async () => {
    setIsSaving(true);
    try {
      const created = await createWorkflow({
        name,
        description,
        status: 'active',
        trigger_type: triggerType,
        nodes,
        edges,
      });
      const execution = await executeWorkflow(created.id, {});
      if (onSelectExecution) onSelectExecution(execution.id);
    } catch (err) {
      alert('Failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('workflows')}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Workflow Studio</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Design autonomous agent pipelines with visual DAG routing
            </p>
          </div>
        </div>

        {/* Template Quick Loaders */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-500 uppercase">Preset:</span>
          <button
            onClick={() => handleSelectTemplate('blank')}
            className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium border border-slate-700 transition-colors"
          >
            Blank
          </button>
          <button
            onClick={() => handleSelectTemplate('email_triage')}
            className="px-2.5 py-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-xs text-blue-400 font-medium border border-blue-500/20 transition-colors"
          >
            Email Triage
          </button>
          <button
            onClick={() => handleSelectTemplate('kpi_digest')}
            className="px-2.5 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-xs text-purple-400 font-medium border border-purple-500/20 transition-colors"
          >
            KPI Digest
          </button>
        </div>
      </div>

      {/* Meta configuration row */}
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Workflow Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-semibold"
          />
        </div>

        <div>
          <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Description
          </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Trigger Type
          </label>
          <select
            value={triggerType}
            onChange={(e) => setTriggerType(e.target.value)}
            className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="manual">Manual Execution</option>
            <option value="webhook">Inbound Webhook</option>
            <option value="schedule">Scheduled Cron</option>
            <option value="event">Internal System Event</option>
          </select>
        </div>
      </div>

      {/* Visual Canvas Builder */}
      <WorkflowBuilder
        nodes={nodes}
        edges={edges}
        onUpdateNodes={setNodes}
        onUpdateEdges={setEdges}
        onSave={handleSave}
        onExecute={handleSaveAndExecute}
        isSaving={isSaving}
      />
    </div>
  );
}
