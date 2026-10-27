import React, { useEffect, useState } from 'react';
import { 
  Activity, Layers, Play, CheckCircle2, XCircle, Clock, 
  ArrowUpRight, Zap, RefreshCw, Plus, Send, ShieldCheck, Cpu 
} from 'lucide-react';
import { fetchDashboardStats, fetchExecutions, fetchWorkflows, executeWorkflow } from '../services/api';
import ExecutionHistory from '../components/ExecutionHistory';
import { formatDuration } from '../utils/formatters';

export default function Dashboard({ onNavigate, onSelectWorkflow, onSelectExecution }) {
  const [stats, setStats] = useState({
    total_workflows: 0,
    active_workflows: 0,
    total_executions: 0,
    completed_executions: 0,
    failed_executions: 0,
    running_executions: 0,
    success_rate_percent: 100.0,
    average_duration_seconds: 0.0,
  });
  const [recentExecutions, setRecentExecutions] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isTriggering, setIsTriggering] = useState(false);

  const loadData = async () => {
    try {
      const [statsData, execData, wfData] = await Promise.all([
        fetchDashboardStats(),
        fetchExecutions({ limit: 8 }),
        fetchWorkflows({ limit: 10 }),
      ]);
      setStats(statsData);
      setRecentExecutions(execData);
      setWorkflows(wfData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleQuickRun = async (workflowId) => {
    setIsTriggering(true);
    try {
      const exec = await executeWorkflow(workflowId, { trigger_source: 'dashboard_quick_run' });
      await loadData();
      if (onSelectExecution) onSelectExecution(exec.id);
    } catch (err) {
      alert('Execution failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsTriggering(false);
    }
  };

  const statCards = [
    {
      label: 'Total Workflows',
      value: stats.total_workflows,
      sub: `${stats.active_workflows} active pipelines`,
      icon: Layers,
      color: 'from-blue-600/20 to-blue-500/5 text-blue-400 border-blue-500/20',
    },
    {
      label: 'Total Executions',
      value: stats.total_executions,
      sub: `${stats.running_executions} active runs`,
      icon: Play,
      color: 'from-indigo-600/20 to-indigo-500/5 text-indigo-400 border-indigo-500/20',
    },
    {
      label: 'Success Rate',
      value: `${stats.success_rate_percent}%`,
      sub: `${stats.completed_executions} passed / ${stats.failed_executions} failed`,
      icon: ShieldCheck,
      color: 'from-emerald-600/20 to-emerald-500/5 text-emerald-400 border-emerald-500/20',
    },
    {
      label: 'Mean Latency',
      value: formatDuration(stats.average_duration_seconds),
      sub: 'Autonomous DAG execution',
      icon: Clock,
      color: 'from-amber-600/20 to-amber-500/5 text-amber-400 border-amber-500/20',
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900 to-indigo-950/30 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-blue-400 uppercase tracking-wider mb-1">
            <Zap className="w-3.5 h-3.5" />
            <span>Autonomous Orchestration Platform</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">AI Workflow Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Monitor multi-agent execution graphs, automated retry policies, quality assertions, and live third-party integrations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('create')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4" />
            <span>Build Workflow</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className={`p-5 rounded-xl border bg-gradient-to-br bg-slate-900/60 backdrop-blur-sm ${card.color} transition-all hover:border-slate-700`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-slate-400">{card.label}</span>
                <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/60">
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-100 font-mono">{card.value}</div>
              <div className="text-[11px] text-slate-400 mt-1">{card.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Quick Launch Active Pipelines */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-200">Active Workflow Pipelines</h3>
            <p className="text-xs text-slate-400">Launch immediate DAG execution runs</p>
          </div>
          <button
            onClick={() => onNavigate('workflows')}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
          >
            <span>View All ({workflows.length})</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflows.slice(0, 3).map((wf) => (
            <div
              key={wf.id}
              className="p-4 rounded-xl border border-slate-800/90 bg-slate-950/60 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                    {wf.trigger_type}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">
                    {wf.nodes?.length || 0} nodes
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-slate-200 truncate">{wf.name}</h4>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">{wf.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <button
                  onClick={() => onSelectWorkflow(wf.id)}
                  className="text-xs text-slate-400 hover:text-slate-200 font-medium"
                >
                  Configure
                </button>
                <button
                  onClick={() => handleQuickRun(wf.id)}
                  disabled={isTriggering}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-sm transition-all disabled:opacity-50"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>Execute</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Executions Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-200">Recent Executions</h3>
            <p className="text-xs text-slate-400">Chronological history of workflow runs and status</p>
          </div>
          <button
            onClick={loadData}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 border border-slate-700"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        <ExecutionHistory
          executions={recentExecutions}
          onSelectExecution={onSelectExecution}
          onRetryExecution={(id) => handleQuickRun(recentExecutions.find(e => e.id === id)?.workflow_id)}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
