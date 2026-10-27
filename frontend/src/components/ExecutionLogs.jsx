import React, { useState, useMemo } from 'react';
import { Terminal, Search, Filter, Copy, Check, Sparkles, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { formatDate } from '../utils/formatters';

export default function ExecutionLogs({ logs = [], isLoading = false }) {
  const [filterLevel, setFilterLevel] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [copied, setCopied] = useState(false);

  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      const matchesLevel = filterLevel === 'ALL' || log.level === filterLevel;
      const matchesSearch = searchQuery === '' || 
        log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (log.node_id && log.node_id.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesLevel && matchesSearch;
    });
  }, [logs, filterLevel, searchQuery]);

  const handleCopyLogs = () => {
    const text = filteredLogs.map(l => `[${l.timestamp}] [${l.level}] ${l.node_id ? `[${l.node_id}] ` : ''}${l.message}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getLevelBadge = (level) => {
    switch (level) {
      case 'AGENT_THOUGHT':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
            <Sparkles className="w-3 h-3" /> THOUGHT
          </span>
        );
      case 'ERROR':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
            <AlertCircle className="w-3 h-3" /> ERROR
          </span>
        );
      case 'WARN':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" /> WARN
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
            <Info className="w-3 h-3" /> INFO
          </span>
        );
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/90 backdrop-blur-md overflow-hidden flex flex-col h-[520px]">
      {/* Log Header Controls */}
      <div className="p-3 sm:p-4 border-b border-slate-800 bg-slate-950/50 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-semibold text-slate-200">Execution Traces & Logs</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
            {filteredLogs.length} events
          </span>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Search bar */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search traces..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700/80 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 w-36 sm:w-48"
            />
          </div>

          {/* Level Filter */}
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700/80 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Levels</option>
            <option value="INFO">Info</option>
            <option value="AGENT_THOUGHT">Agent Thoughts</option>
            <option value="WARN">Warnings</option>
            <option value="ERROR">Errors</option>
          </select>

          {/* Copy logs */}
          <button
            onClick={handleCopyLogs}
            disabled={filteredLogs.length === 0}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition-colors border border-slate-700 disabled:opacity-50"
            title="Copy logs"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Logs Stream Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-xs bg-slate-950/80 select-text">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-slate-500">
            <span className="animate-pulse">Loading live execution logs...</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-2">
            <Terminal className="w-8 h-8 opacity-40" />
            <p>No log records recorded for this execution.</p>
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className={`p-2.5 rounded-lg border transition-all ${
                log.level === 'AGENT_THOUGHT'
                  ? 'bg-purple-950/20 border-purple-900/40 text-purple-200'
                  : log.level === 'ERROR'
                  ? 'bg-rose-950/20 border-rose-900/40 text-rose-200'
                  : log.level === 'WARN'
                  ? 'bg-amber-950/20 border-amber-900/40 text-amber-200'
                  : 'bg-slate-900/60 border-slate-800/80 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <div className="flex items-center gap-2">
                  {getLevelBadge(log.level)}
                  {log.node_id && (
                    <span className="text-[10px] text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded border border-blue-500/20">
                      {log.node_id}
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-slate-500">
                  {formatDate(log.timestamp)}
                </span>
              </div>
              <p className="whitespace-pre-wrap break-words leading-relaxed pl-1">
                {log.message}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
