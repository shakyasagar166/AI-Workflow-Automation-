import React, { useState } from 'react';
import { 
  Plus, Play, Save, Code, Zap, Brain, Cpu, ShieldCheck, 
  GitFork, Mail, Globe, Clock, ArrowRight, Settings, X 
} from 'lucide-react';
import WorkflowNode from './WorkflowNode';
import { NODE_TYPES } from '../utils/constants';

export default function WorkflowBuilder({
  nodes = [],
  edges = [],
  onUpdateNodes,
  onUpdateEdges,
  onSave,
  onExecute,
  isSaving = false,
}) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [connectingSource, setConnectingSource] = useState(null);

  const handleAddNode = (typeMeta) => {
    const id = `node_${Date.now()}`;
    const newNode = {
      id,
      type: typeMeta.type,
      name: `${typeMeta.label} ${nodes.length + 1}`,
      config: JSON.parse(JSON.stringify(typeMeta.defaultConfig || {})),
      position: {
        x: 80 + (nodes.length % 4) * 300,
        y: 100 + Math.floor(nodes.length / 4) * 220,
      },
    };

    const nextNodes = [...nodes, newNode];
    onUpdateNodes(nextNodes);

    // Auto-connect sequentially if previous node exists
    if (nodes.length > 0) {
      const prevNode = nodes[nodes.length - 1];
      const newEdge = {
        id: `e_${prevNode.id}_${newNode.id}`,
        source: prevNode.id,
        target: newNode.id,
      };
      onUpdateEdges([...edges, newEdge]);
    }

    setSelectedNode(newNode);
  };

  const handleDeleteNode = (nodeId) => {
    onUpdateNodes(nodes.filter((n) => n.id !== nodeId));
    onUpdateEdges(edges.filter((e) => e.source !== nodeId && e.target !== nodeId));
    if (selectedNode?.id === nodeId) setSelectedNode(null);
  };

  const handleUpdateConfig = (key, value) => {
    if (!selectedNode) return;
    const updated = {
      ...selectedNode,
      config: {
        ...selectedNode.config,
        [key]: value,
      },
    };
    setSelectedNode(updated);
    onUpdateNodes(nodes.map((n) => (n.id === updated.id ? updated : n)));
  };

  const handleUpdateName = (name) => {
    if (!selectedNode) return;
    const updated = { ...selectedNode, name };
    setSelectedNode(updated);
    onUpdateNodes(nodes.map((n) => (n.id === updated.id ? updated : n)));
  };

  return (
    <div className="flex flex-col h-[750px] rounded-xl border border-slate-800 bg-slate-950 overflow-hidden shadow-2xl relative">
      {/* Builder Top Toolbar */}
      <div className="h-14 px-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-slate-300 font-mono uppercase tracking-wider">
            Canvas Nodes: {nodes.length} | Edges: {edges.length}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowJsonModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition-colors"
          >
            <Code className="w-3.5 h-3.5" />
            <span>View JSON</span>
          </button>

          {onExecute && (
            <button
              onClick={onExecute}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-md shadow-emerald-600/20 transition-all"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Run Pipeline</span>
            </button>
          )}

          {onSave && (
            <button
              onClick={onSave}
              disabled={isSaving}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{isSaving ? 'Saving...' : 'Save Workflow'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Builder Body */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Toolbox */}
        <aside className="w-64 border-r border-slate-800 bg-slate-900/40 p-4 overflow-y-auto space-y-4">
          <div>
            <h5 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 font-mono">
              Add Workflow Nodes
            </h5>
            <div className="space-y-1.5">
              {NODE_TYPES.map((typeMeta) => (
                <button
                  key={typeMeta.type}
                  onClick={() => handleAddNode(typeMeta)}
                  className="w-full text-left p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-800/90 border border-slate-800 hover:border-slate-700 transition-all group flex items-start gap-2.5"
                >
                  <div className={`p-1.5 rounded-md bg-gradient-to-br border ${typeMeta.color} mt-0.5`}>
                    <Plus className="w-3.5 h-3.5" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-slate-200 group-hover:text-blue-400 transition-colors">
                      {typeMeta.label}
                    </p>
                    <p className="text-[10px] text-slate-500 truncate">{typeMeta.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Visual Canvas Area */}
        <div className="flex-1 relative overflow-auto bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:20px_20px] p-8 min-w-[1200px] min-h-[900px]">
          {/* Connection Lines (SVG) */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            {edges.map((edge) => {
              const srcNode = nodes.find((n) => n.id === edge.source);
              const tgtNode = nodes.find((n) => n.id === edge.target);
              if (!srcNode || !tgtNode) return null;

              const x1 = (srcNode.position?.x || 100) + 288;
              const y1 = (srcNode.position?.y || 100) + 65;
              const x2 = tgtNode.position?.x || 400;
              const y2 = (tgtNode.position?.y || 100) + 65;

              const dx = (x2 - x1) / 2;
              const pathData = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

              return (
                <g key={edge.id}>
                  <path
                    d={pathData}
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="2.5"
                    strokeDasharray={edge.condition ? '5 5' : 'none'}
                    className="opacity-70"
                  />
                  <circle cx={x2 - 4} cy={y2} r="4" fill="#3b82f6" />
                </g>
              );
            })}
          </svg>

          {/* Node Elements */}
          {nodes.length === 0 ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
              <Zap className="w-12 h-12 text-slate-700 mb-3" />
              <h4 className="text-base font-semibold text-slate-400">Your Workflow Canvas is Empty</h4>
              <p className="text-xs text-slate-500 mt-1 max-w-sm text-center">
                Click on any node from the left toolbox to add Trigger, AI Agents, or Integrations.
              </p>
            </div>
          ) : (
            nodes.map((node) => (
              <WorkflowNode
                key={node.id}
                node={node}
                isSelected={selectedNode?.id === node.id}
                onSelect={(n) => setSelectedNode(n)}
                onDelete={handleDeleteNode}
              />
            ))
          )}
        </div>

        {/* Right Inspector Drawer (Active when a node is selected) */}
        {selectedNode && (
          <aside className="w-80 border-l border-slate-800 bg-slate-900/90 backdrop-blur-md p-5 overflow-y-auto space-y-5 z-20">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-blue-400" />
                <h4 className="text-sm font-semibold text-slate-200">Node Properties</h4>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded-md text-slate-500 hover:text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Label input */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                Node Name
              </label>
              <input
                type="text"
                value={selectedNode.name || ''}
                onChange={(e) => handleUpdateName(e.target.value)}
                className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
              />
            </div>

            {/* Config Fields according to type */}
            {selectedNode.type === 'agent_planner' && (
              <div>
                <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                  High-Level Objective / Goal
                </label>
                <textarea
                  rows={4}
                  value={selectedNode.config?.goal || ''}
                  onChange={(e) => handleUpdateConfig('goal', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
                  placeholder="Specify planning goals..."
                />
              </div>
            )}

            {selectedNode.type === 'agent_executor' && (
              <>
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                    Task Instruction
                  </label>
                  <textarea
                    rows={4}
                    value={selectedNode.config?.instruction || ''}
                    onChange={(e) => handleUpdateConfig('instruction', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
                    placeholder="Instructions for execution agent..."
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                    System Role
                  </label>
                  <input
                    type="text"
                    value={selectedNode.config?.system_role || ''}
                    onChange={(e) => handleUpdateConfig('system_role', e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </>
            )}

            {selectedNode.type === 'agent_verifier' && (
              <div>
                <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                  Minimum Confidence Threshold (0.0 - 1.0)
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.5"
                  max="1.0"
                  value={selectedNode.config?.minimum_confidence || 0.85}
                  onChange={(e) => handleUpdateConfig('minimum_confidence', parseFloat(e.target.value))}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>
            )}

            {selectedNode.type === 'integration_email' && (
              <>
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                    Recipient Email
                  </label>
                  <input
                    type="text"
                    value={selectedNode.config?.to_email || ''}
                    onChange={(e) => handleUpdateConfig('to_email', e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                    Subject Line
                  </label>
                  <input
                    type="text"
                    value={selectedNode.config?.subject || ''}
                    onChange={(e) => handleUpdateConfig('subject', e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </>
            )}

            {selectedNode.type === 'integration_webhook' && (
              <div>
                <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                  Target Endpoint URL
                </label>
                <input
                  type="text"
                  value={selectedNode.config?.url || ''}
                  onChange={(e) => handleUpdateConfig('url', e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>
            )}
          </aside>
        )}
      </div>

      {/* JSON Schema Preview Modal */}
      {showJsonModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full p-5 shadow-2xl flex flex-col max-h-[85vh]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-semibold text-slate-200">Workflow JSON Definition</h3>
              <button
                onClick={() => setShowJsonModal(false)}
                className="p-1 rounded-md text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <pre className="flex-1 overflow-auto bg-slate-950 p-4 rounded-lg my-4 text-xs font-mono text-slate-300 border border-slate-800/80">
              {JSON.stringify({ nodes, edges }, null, 2)}
            </pre>
            <div className="flex justify-end">
              <button
                onClick={() => setShowJsonModal(false)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
