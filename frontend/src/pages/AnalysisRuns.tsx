import React, { useState, useEffect } from 'react';
import {
  History,
  Play,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Terminal,
  Clock,
  Coins,
  Cpu
} from 'lucide-react';
import { fetchRuns, triggerRun, fetchRunLogs } from '../services/api';

export const AnalysisRuns: React.FC = () => {
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [selectedRun, setSelectedRun] = useState<any | null>(null);
  const [logs, setLogs] = useState<string>('');

  const loadRuns = async () => {
    try {
      setLoading(true);
      const res = await fetchRuns();
      setRuns(res.runs || []);
      if (res.runs?.length > 0 && !selectedRun) {
        setSelectedRun(res.runs[0]);
        setLogs(res.runs[0].logs || '');
      }
    } catch (err: any) {
      console.error('Failed to load runs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRuns();
  }, []);

  const handleSelectRun = async (run: any) => {
    setSelectedRun(run);
    try {
      const res = await fetchRunLogs(run.run_id);
      setLogs(res.logs || run.logs || '');
    } catch (e) {
      setLogs(run.logs || '');
    }
  };

  const handleTrigger = async () => {
    try {
      setTriggering(true);
      const newRun = await triggerRun();
      await loadRuns();
      setSelectedRun(newRun);
      setLogs(newRun.logs || '');
    } catch (err: any) {
      alert('Error triggering run: ' + err.message);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Analysis Runs & Audit History</h2>
          <p className="text-sm text-slate-500 mt-1">
            Persisted execution ledger, dataset fingerprints, and LLM token cost accounting
          </p>
        </div>
        <button
          onClick={handleTrigger}
          disabled={triggering}
          className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-md hover:bg-slate-800 disabled:opacity-50 transition flex items-center space-x-2 shadow-sm"
        >
          <Play className={`w-4 h-4 ${triggering ? 'animate-spin' : ''}`} />
          <span>{triggering ? 'Auditing Corpus...' : 'Execute Analysis Run'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Runs List */}
        <div className="space-y-3">
          {runs.map((r) => {
            const isSelected = selectedRun?.run_id === r.run_id;
            return (
              <div
                key={r.run_id}
                onClick={() => handleSelectRun(r)}
                className={`p-4 rounded-lg border transition cursor-pointer ${
                  isSelected
                    ? 'bg-white border-[#B76E79] shadow-md ring-1 ring-[#B76E79]'
                    : 'bg-white border-slate-200 hover:border-[#E8D7D8] shadow-sm'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-slate-900">{r.run_id}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      r.status === 'COMPLETED'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}
                  >
                    {r.status}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-100 text-center font-mono">
                  <div>
                    <div className="text-[10px] text-slate-400">Total</div>
                    <div className="text-xs font-bold text-slate-800">{r.total_cases}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-emerald-600">Complete</div>
                    <div className="text-xs font-bold text-emerald-700">{r.complete_cases}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-rose-600">Incomplete</div>
                    <div className="text-xs font-bold text-rose-700">{r.incomplete_cases}</div>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>{r.completed_at?.slice(11, 19)} UTC</span>
                  <span>${Number(r.estimated_cost_usd || 0).toFixed(4)} USD</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Run Details & Execution Log Stream */}
        <div className="lg:col-span-2 space-y-6">
          {selectedRun ? (
            <>
              {/* Telemetry Bar */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <Cpu className="w-4 h-4 text-slate-400" />
                    <span>Engine & Model</span>
                  </div>
                  <div className="font-mono text-xs font-bold text-slate-800 mt-1">
                    {selectedRun.model_provider} / {selectedRun.model_identifier}
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <Coins className="w-4 h-4 text-slate-400" />
                    <span>Token & Cost Accounting</span>
                  </div>
                  <div className="font-mono text-xs font-bold text-slate-800 mt-1">
                    {selectedRun.total_tokens} tok / ${Number(selectedRun.estimated_cost_usd || 0).toFixed(4)}
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <Clock className="w-4 h-4 text-slate-400" />
                    <span>Completed At</span>
                  </div>
                  <div className="font-mono text-xs font-bold text-slate-800 mt-1">
                    {selectedRun.completed_at?.slice(0, 19).replace('T', ' ')}
                  </div>
                </div>
              </div>

              {/* Execution Logs Terminal */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-3 bg-slate-900 border-b border-slate-800 text-xs text-slate-300 font-mono flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Terminal className="w-4 h-4 text-[#E8A598]" />
                    <span>Execution Stream — {selectedRun.run_id}</span>
                  </div>
                  <span className="text-[10px] text-slate-500">Structured Output Logs</span>
                </div>
                <div className="p-4 bg-slate-950 font-mono text-xs text-slate-300 overflow-x-auto max-h-[450px]">
                  <pre className="whitespace-pre-wrap">{logs || selectedRun.logs || 'No logs available.'}</pre>
                </div>
              </div>
            </>
          ) : (
            <div className="p-8 text-center text-slate-400 bg-white rounded-lg border border-slate-200">
              Select an analysis run to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
