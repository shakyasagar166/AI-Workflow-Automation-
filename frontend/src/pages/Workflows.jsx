import React, { useState, useEffect } from 'react';
import { 
  Layers, Search, Plus, Play, Download, Upload, Trash2, 
  ExternalLink, Filter, Zap, MoreVertical, X 
} from 'lucide-react';
import { fetchWorkflows, deleteWorkflow, executeWorkflow, importWorkflowTemplate } from '../services/api';
import { formatDate } from '../utils/formatters';

export default function Workflows({ onNavigate, onSelectWorkflow, onSelectExecution }) {
  const [workflows, setWorkflows] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importJsonText, setImportJsonText] = useState('');

  const loadWorkflows = async () => {
    setIsLoading(true);
    try {
      const data = await fetchWorkflows();
      setWorkflows(data);
    } catch (err) {
      console.error('Failed to fetch workflows:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadWorkflows();
  }, []);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete workflow "${name}"?`)) return;
    try {
      await deleteWorkflow(id);
      setWorkflows(workflows.filter((w) => w.id !== id));
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleRun = async (id) => {
    try {
      const execution = await executeWorkflow(id, {});
      if (onSelectExecution) onSelectExecution(execution.id);
    } catch (err) {
      alert('Execution failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleImportSubmit = async () => {
    try {
      const parsed = JSON.parse(importJsonText);
      await importWorkflowTemplate(parsed);
      setShowImportModal(false);
      setImportJsonText('');
      loadWorkflows();
    } catch (err) {
      alert('Invalid JSON template or import failed: ' + err.message);
    }
  };

  const filteredWorkflows = workflows.filter((w) => {
    const matchesSearch = searchQuery === '' || 
      w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (w.description && w.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'ALL' || w.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Workflow Management</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Create, configure, and orchestrate DAG pipelines and AI agents
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowImportModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all"
          >
            <Upload className="w-4 h-4" />
            <span>Import Template</span>
          </button>

          <button
            onClick={() => onNavigate('create')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/20 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4" />
            <span>New Workflow</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search workflows by title or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          <span className="text-xs text-slate-500">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="active">Active</option>
            <option value="draft">Draft</option>
            <option value="paused">Paused</option>
          </select>
        </div>
      </div>

      {/* Workflow Grid */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-500">Loading workflows...</div>
      ) : filteredWorkflows.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-12 text-center">
          <Layers className="w-12 h-12 text-slate-700 mx-auto mb-3" />
          <h4 className="text-sm font-semibold text-slate-300">No matching workflows</h4>
          <p className="text-xs text-slate-500 mt-1">Try clearing your filters or create a new pipeline.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredWorkflows.map((wf) => (
            <div
              key={wf.id}
              onClick={() => onSelectWorkflow(wf.id)}
              className="rounded-xl border border-slate-800 bg-slate-900/70 hover:border-slate-700 hover:shadow-xl transition-all p-5 flex flex-col justify-between cursor-pointer group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">
                    {wf.trigger_type}
                  </span>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                    wf.status === 'active' 
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {wf.status}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-100 group-hover:text-blue-400 transition-colors line-clamp-1">
                  {wf.name}
                </h3>
                <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                  {wf.description || 'No description provided.'}
                </p>

                <div className="mt-4 flex items-center gap-4 text-[11px] font-mono text-slate-500">
                  <span>{wf.nodes?.length || 0} nodes</span>
                  <span>{wf.edges?.length || 0} edges</span>
                  <span>{formatDate(wf.updated_at)}</span>
                </div>
              </div>

              {/* Bottom Actions */}
              <div 
                className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  onClick={() => handleDelete(wf.id, wf.name)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onSelectWorkflow(wf.id)}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors"
                  >
                    View Details
                  </button>

                  <button
                    onClick={() => handleRun(wf.id)}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-sm shadow-emerald-600/20 transition-all"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Run</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-xl w-full p-5 shadow-2xl flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-semibold text-slate-200">Import Workflow Template (JSON)</h3>
              <button
                onClick={() => setShowImportModal(false)}
                className="p-1 rounded-md text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <textarea
              rows={12}
              placeholder="Paste JSON template here..."
              value={importJsonText}
              onChange={(e) => setImportJsonText(e.target.value)}
              className="w-full my-4 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:border-blue-500"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowImportModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleImportSubmit}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white"
              >
                Import Workflow
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
