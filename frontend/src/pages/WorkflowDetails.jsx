import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, Play, RotateCw, Clock, CheckCircle2, XCircle, 
  Settings, Terminal, Download, Code, Sparkles, Layers, X 
} from 'lucide-react';
import { 
  fetchWorkflowById, executeWorkflow, fetchExecutions, 
  fetchExecutionById, fetchExecutionLogs, retryExecution 
} from '../services/api';
import WorkflowNode from '../components/WorkflowNode';
import ExecutionHistory from '../components/ExecutionHistory';
import ExecutionLogs from '../components/ExecutionLogs';
import { formatDate, formatDuration } from '../utils/formatters';
import { STATUS_STYLES } from '../utils/constants';

export default function WorkflowDetails({
  workflowId,
  selectedExecutionId,
  onNavigate,
  onSelectExecution,
}) {
  const [workflow, setWorkflow] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [activeExecution, setActiveExecution] = useState(null);
  const [activeLogs, setActiveLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);
  const [showTriggerModal, setShowTriggerModal] = useState(false);
  const [customPayloadText, setCustomPayloadText] = useState('{\n  "query": "Sample customer query"\n}');

  const loadWorkflowData = async () => {
    try {
      const [wf, execs] = await Promise.all([
        fetchWorkflowById(workflowId),
        fetchExecutions({ workflow_id: workflowId, limit: 15 }),
      ]);
      setWorkflow(wf);
      setExecutions(execs);

      // Default to selectedExecutionId or most recent
      const execToLoad = selectedExecutionId || (execs.length > 0 ? execs[0].id : null);
      if (execToLoad) {
        loadExecutionDetails(execToLoad);
      }
    } catch (err) {
      console.error('Failed to load workflow details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadExecutionDetails = async (execId) => {
    try {
      const [execData, logsData] = await Promise.all([
        fetchExecutionById(execId),
        fetchExecutionLogs(execId),
      ]);
      setActiveExecution(execData);
      setActiveLogs(logsData);
    } catch (err) {
      console.error('Failed to load execution details:', err);
    }
  };

  useEffect(() => {
    loadWorkflowData();
  }, [workflowId, selectedExecutionId]);

  // Polling when active execution is running
  useEffect(() => {
    if (activeExecution?.status === 'RUNNING' || activeExecution?.status === 'PENDING') {
      const interval = setInterval(() => {
        loadExecutionDetails(activeExecution.id);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [activeExecution?.status]);

  const handleTriggerRun = async () => {
    setIsExecuting(true);
    try {
      let parsedPayload = {};
      try {
        parsedPayload = JSON.parse(customPayloadText);
      } catch {
        alert('Invalid JSON in custom payload. Using empty object.');
      }

      const exec = await executeWorkflow(workflowId, parsedPayload, false);
      setShowTriggerModal(false);
      await loadWorkflowData();
      loadExecutionDetails(exec.id);
    } catch (err) {
      alert('Execution failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRetry = async (execId) => {
    try {
      const newExec = await retryExecution(execId);
      await loadWorkflowData();
      loadExecutionDetails(newExec.id);
    } catch (err) {
      alert('Retry failed: ' + err.message);
    }
  };

  if (isLoading || !workflow) {
    return (
      <div className="p-12 text-center text-slate-500">
        Loading workflow pipeline...
      </div>
    );
  }

  // Create a map of step statuses from the active execution
  const stepStatusMap = {};
  if (activeExecution?.step_executions) {
    activeExecution.step_executions.forEach((step) => {
      stepStatusMap[step.node_id] = step;
    });
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-xl border border-slate-800 bg-slate-900/70 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('workflows')}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-100">{workflow.name}</h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                {workflow.trigger_type}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{workflow.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowTriggerModal(true)}
            disabled={isExecuting}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-lg shadow-emerald-600/20 transition-all disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isExecuting ? 'Running...' : 'Execute Workflow'}</span>
          </button>
        </div>
      </div>

      {/* Visual DAG Canvas View */}
      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800 text-xs text-slate-400 font-mono">
          <span>PIPELINE GRAPH TOPOLOGY ({workflow.nodes?.length} NODES)</span>
          {activeExecution && (
            <span className="flex items-center gap-2">
              <span>Run Status:</span>
              <span className={`px-2 py-0.5 rounded-full border text-[11px] font-semibold ${STATUS_STYLES[activeExecution.status] || ''}`}>
                {activeExecution.status}
              </span>
            </span>
          )}
        </div>

        <div className="relative overflow-auto min-h-[380px] bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:20px_20px] rounded-lg p-6">
          {/* Edge lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            {workflow.edges?.map((edge) => {
              const srcNode = workflow.nodes?.find((n) => n.id === edge.source);
              const tgtNode = workflow.nodes?.find((n) => n.id === edge.target);
              if (!srcNode || !tgtNode) return null;

              const x1 = (srcNode.position?.x || 100) + 288;
              const y1 = (srcNode.position?.y || 100) + 65;
              const x2 = tgtNode.position?.x || 400;
              const y2 = (tgtNode.position?.y || 100) + 65;

              const dx = (x2 - x1) / 2;
              const pathData = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

              const targetStatus = stepStatusMap[edge.target]?.status;
              const strokeColor = targetStatus === 'COMPLETED' ? '#10b981' : targetStatus === 'RUNNING' ? '#3b82f6' : '#475569';

              return (
                <path
                  key={edge.id}
                  d={pathData}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth="2.5"
                  strokeDasharray={edge.condition ? '5 5' : 'none'}
                  className="opacity-80"
                />
              );
            })}
          </svg>

          {/* Render nodes with active execution states */}
          <div className="min-w-[1200px] min-h-[340px] relative">
            {workflow.nodes?.map((node) => {
              const stepInfo = stepStatusMap[node.id];
              return (
                <WorkflowNode
                  key={node.id}
                  node={node}
                  isDraggable={false}
                  executionStatus={stepInfo?.status}
                  stepData={stepInfo}
                />
              );
            })}
          </div>
        </div>
      </div>

      {/* Execution Trace & Logs Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Execution Run Details / Summary */}
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Execution Run Inspector</h3>
            {activeExecution ? (
              <div className="space-y-3 text-xs font-mono">
                <div>
                  <span className="text-slate-500 block">Execution ID:</span>
                  <span className="text-blue-400 break-all">{activeExecution.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Status:</span>
                  <span className={`px-2 py-0.5 rounded-full border text-[11px] font-semibold ${STATUS_STYLES[activeExecution.status] || ''}`}>
                    {activeExecution.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Duration:</span>
                  <span className="text-slate-300">{formatDuration(activeExecution.duration_seconds)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Trigger:</span>
                  <span className="text-slate-300">{activeExecution.trigger}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Started:</span>
                  <span className="text-slate-300">{formatDate(activeExecution.started_at)}</span>
                </div>

                {activeExecution.result && (
                  <div className="pt-3 border-t border-slate-800">
                    <span className="text-slate-400 font-semibold block mb-1">Output Summary:</span>
                    <pre className="bg-slate-950 p-2.5 rounded text-[11px] text-emerald-400 overflow-x-auto max-h-36">
                      {JSON.stringify(activeExecution.result, null, 2)}
                    </pre>
                  </div>
                )}

                {activeExecution.error && (
                  <div className="pt-3 border-t border-slate-800">
                    <span className="text-rose-400 font-semibold block mb-1">Failure Trace:</span>
                    <p className="bg-rose-950/20 border border-rose-900/40 p-2.5 rounded text-[11px] text-rose-300">
                      {activeExecution.error}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500">Select an execution to inspect output and traces.</p>
            )}
          </div>

          {/* Past Executions for this workflow */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
            <h4 className="text-xs font-semibold text-slate-300 mb-3 uppercase tracking-wider font-mono">
              Pipeline Runs ({executions.length})
            </h4>
            <div className="space-y-1.5 max-h-60 overflow-y-auto">
              {executions.map((e) => (
                <button
                  key={e.id}
                  onClick={() => loadExecutionDetails(e.id)}
                  className={`w-full text-left p-2 rounded-lg border transition-all flex items-center justify-between text-xs font-mono ${
                    activeExecution?.id === e.id
                      ? 'bg-blue-600/15 border-blue-500/40 text-blue-300'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400'
                  }`}
                >
                  <span className="truncate">{e.id.slice(0, 8)}...</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded border ${STATUS_STYLES[e.status] || ''}`}>
                    {e.status}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right 2 cols: Live Execution Logs */}
        <div className="lg:col-span-2">
          <ExecutionLogs logs={activeLogs} />
        </div>
      </div>

      {/* Trigger Modal with Custom Payload */}
      {showTriggerModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-5 shadow-2xl flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-semibold text-slate-200">Trigger Pipeline Run</h3>
              <button
                onClick={() => setShowTriggerModal(false)}
                className="p-1 rounded-md text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="my-4 space-y-2">
              <label className="block text-xs font-mono text-slate-400">
                Trigger JSON Payload (Passed to entrypoint Trigger Node)
              </label>
              <textarea
                rows={6}
                value={customPayloadText}
                onChange={(e) => setCustomPayloadText(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowTriggerModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleTriggerRun}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-sm"
              >
                Start Execution
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
