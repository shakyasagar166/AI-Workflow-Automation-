import React from 'react';
import { Play, RotateCw, Clock, CheckCircle2, XCircle, AlertCircle, Eye, ExternalLink } from 'lucide-react';
import { formatDate, formatDuration } from '../utils/formatters';
import { STATUS_STYLES } from '../utils/constants';

export default function ExecutionHistory({
  executions = [],
  onSelectExecution,
  onRetryExecution,
  isLoading = false,
}) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'FAILED':
        return <XCircle className="w-4 h-4 text-rose-400" />;
      case 'RUNNING':
        return <RotateCw className="w-4 h-4 text-blue-400 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-amber-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-500 animate-pulse">
        Loading execution history...
      </div>
    );
  }

  if (executions.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-12 text-center">
        <Clock className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <h4 className="text-sm font-semibold text-slate-300">No Executions Found</h4>
        <p className="text-xs text-slate-500 mt-1">Trigger a manual run or send a webhook event to start.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/60 text-[11px] font-semibold text-slate-400 uppercase tracking-wider font-mono">
              <th className="py-3 px-4">Execution ID</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Trigger</th>
              <th className="py-3 px-4">Duration</th>
              <th className="py-3 px-4">Started At</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {executions.map((exec) => {
              const statusClass = STATUS_STYLES[exec.status] || 'bg-slate-800 text-slate-300';
              return (
                <tr
                  key={exec.id}
                  onClick={() => onSelectExecution && onSelectExecution(exec.id)}
                  className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                >
                  <td className="py-3.5 px-4 font-mono font-medium text-slate-200">
                    <span className="text-blue-400 group-hover:underline">
                      {exec.id.slice(0, 8)}...
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] font-medium ${statusClass}`}>
                      {getStatusIcon(exec.status)}
                      <span>{exec.status}</span>
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px] border border-slate-700/60">
                      {exec.trigger || 'manual'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">
                    {formatDuration(exec.duration_seconds)}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">
                    {formatDate(exec.started_at || exec.created_at)}
                  </td>
                  <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => onSelectExecution && onSelectExecution(exec.id)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700"
                        title="View Details"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      {onRetryExecution && (
                        <button
                          onClick={() => onRetryExecution(exec.id)}
                          className="p-1.5 rounded-lg bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 hover:text-blue-300 transition-colors border border-blue-500/20"
                          title="Rerun Execution"
                        >
                          <RotateCw className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
