import React from 'react';
import { 
  Zap, Brain, Cpu, ShieldCheck, GitFork, Mail, Globe, Clock, 
  Trash2, Settings2, CheckCircle2, AlertCircle, RefreshCw 
} from 'lucide-react';
import { NODE_TYPES, STATUS_STYLES } from '../utils/constants';

const ICON_MAP = {
  Zap,
  Brain,
  Cpu,
  ShieldCheck,
  GitFork,
  Mail,
  Globe,
  Clock,
};

export default function WorkflowNode({
  node,
  isSelected,
  onSelect,
  onDelete,
  executionStatus,
  stepData,
  isDraggable = true,
  onDragStart,
}) {
  const typeMeta = NODE_TYPES.find((t) => t.type === node.type) || {
    label: node.type,
    color: 'from-slate-500/20 to-slate-600/10 border-slate-600 text-slate-300',
    icon: 'Cpu',
  };

  const IconComponent = ICON_MAP[typeMeta.icon] || Cpu;
  const statusBadge = executionStatus ? STATUS_STYLES[executionStatus] || 'bg-slate-800 text-slate-400' : null;

  return (
    <div
      draggable={isDraggable}
      onDragStart={onDragStart}
      onClick={() => onSelect && onSelect(node)}
      className={`relative w-72 rounded-xl border bg-slate-900/90 backdrop-blur-sm p-4 shadow-xl transition-all cursor-pointer ${
        isSelected
          ? 'ring-2 ring-blue-500 border-blue-500 shadow-blue-500/20'
          : 'border-slate-800 hover:border-slate-700 hover:shadow-2xl'
      }`}
      style={{
        transform: node.position ? `translate(${node.position.x}px, ${node.position.y}px)` : undefined,
        position: node.position ? 'absolute' : 'relative',
      }}
    >
      {/* Node Header */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className={`p-2 rounded-lg bg-gradient-to-br border ${typeMeta.color}`}>
            <IconComponent className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h4 className="text-sm font-semibold text-slate-100 truncate">
              {node.name || typeMeta.label}
            </h4>
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              {typeMeta.label}
            </span>
          </div>
        </div>

        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(node.id);
            }}
            className="p-1 rounded-md text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            title="Delete Node"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Node Body / Configuration summary */}
      <div className="bg-slate-950/60 rounded-lg p-2.5 border border-slate-800/80 text-xs text-slate-400 font-mono space-y-1">
        {node.type === 'trigger' && (
          <p className="truncate">Payload: {Object.keys(node.config?.default_payload || {}).length} keys defined</p>
        )}
        {node.type === 'agent_planner' && (
          <p className="truncate">Goal: {node.config?.goal || 'Auto-decompose'}</p>
        )}
        {node.type === 'agent_executor' && (
          <p className="truncate">Prompt: {node.config?.instruction || 'Process inputs'}</p>
        )}
        {node.type === 'agent_verifier' && (
          <p className="truncate">Min Conf: {node.config?.minimum_confidence || 0.85}</p>
        )}
        {node.type === 'integration_email' && (
          <p className="truncate">To: {node.config?.to_email || 'Recipient'}</p>
        )}
        {node.type === 'integration_webhook' && (
          <p className="truncate">URL: {node.config?.url || 'https://...'}</p>
        )}
        {node.type === 'condition' && (
          <p className="truncate">Rule: {node.config?.operator || '=='} {node.config?.right_value || 'true'}</p>
        )}
      </div>

      {/* Execution status indicator (when viewing details / live run) */}
      {executionStatus && (
        <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/80">
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${statusBadge}`}>
            {executionStatus}
          </span>
          {stepData?.duration_seconds !== undefined && (
            <span className="text-[10px] font-mono text-slate-400">
              {stepData.duration_seconds < 1 
                ? `${Math.round(stepData.duration_seconds * 1000)}ms` 
                : `${stepData.duration_seconds.toFixed(2)}s`}
            </span>
          )}
        </div>
      )}

      {/* Connector Ports Visual */}
      <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-slate-800 border-2 border-slate-600 flex items-center justify-center">
        <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
      </div>
      <div className="absolute -right-2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-slate-800 border-2 border-blue-500 flex items-center justify-center">
        <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
      </div>
    </div>
  );
}
