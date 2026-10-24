import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  AlertOctagon,
  MinusCircle,
  Clock,
  Play,
  ArrowRight,
  Database,
  ExternalLink,
  Layers,
  FileCheck
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { fetchOverview, triggerRun, OverviewMetrics } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

interface OverviewProps {
  onNavigate: (tab: string, caseId?: string) => void;
  onOpenUpload?: () => void;
}

export const Overview: React.FC<OverviewProps> = ({ onNavigate, onOpenUpload }) => {
  const [data, setData] = useState<OverviewMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await fetchOverview();
      setData(res);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunAnalysis = async () => {
    try {
      setTriggering(true);
      await triggerRun();
      await loadData();
    } catch (err: any) {
      alert('Error triggering run: ' + err.message);
    } finally {
      setTriggering(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-[#EAC5CB] border-t-[#B76E79] rounded-full animate-spin" />
          <span className="text-sm text-[#8C6D73] font-medium">Loading forensic audit state...</span>
        </div>
      </div>
    );
  }

  const chartData = [
    { name: 'Complete', value: data?.complete_count || 0, color: '#10B981' },
    { name: 'Incomplete (Ghost Data)', value: data?.incomplete_count || 0, color: '#F43F5E' },
    { name: 'Not Applicable', value: data?.not_applicable_count || 0, color: '#94A3B8' },
  ].filter(d => d.value > 0);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header & Quick Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Audit Operations Dashboard</h2>
          <p className="text-sm text-slate-500 mt-1">
            Northstar Shop — Distributed Data Erasure Forensic Verification
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {onOpenUpload && (
            <button
              onClick={onOpenUpload}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition shadow-sm flex items-center space-x-1.5"
            >
              <span>Upload Custom CSV</span>
            </button>
          )}
          <button
            onClick={() => onNavigate('cases')}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition shadow-sm"
          >
            Explore 518 Cases
          </button>
          <button
            onClick={handleRunAnalysis}
            disabled={triggering}
            className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-md hover:bg-slate-800 disabled:opacity-50 transition flex items-center space-x-2 shadow-sm"
          >
            <Play className={`w-4 h-4 ${triggering ? 'animate-spin' : ''}`} />
            <span>{triggering ? 'Auditing Corpus...' : 'Execute Full Audit'}</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider">
            <span>Total Requests</span>
            <Database className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-3xl font-bold text-slate-900 mt-2 font-mono">{data?.total_requests || 0}</div>
          <div className="text-xs text-slate-500 mt-1">Full dataset test scope</div>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-emerald-700 text-xs font-semibold uppercase tracking-wider">
            <span>Verified Complete</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-3xl font-bold text-emerald-700 mt-2 font-mono">{data?.complete_count || 0}</div>
          <div className="text-xs text-slate-500 mt-1">100% compliant at cutoff</div>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-rose-700 text-xs font-semibold uppercase tracking-wider">
            <span>Incomplete / Ghost Data</span>
            <AlertOctagon className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-3xl font-bold text-rose-700 mt-2 font-mono">{data?.incomplete_count || 0}</div>
          <div className="text-xs text-slate-500 mt-1">Active risks & unpurged records</div>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-600 text-xs font-semibold uppercase tracking-wider">
            <span>Not Applicable</span>
            <MinusCircle className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-3xl font-bold text-slate-700 mt-2 font-mono">{data?.not_applicable_count || 0}</div>
          <div className="text-xs text-slate-500 mt-1">Non-deletion exports/inquiries</div>
        </div>
      </div>

      {/* Center Layout: Chart + System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Compliance Breakdown Chart */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Audited Status Distribution</h3>
            <p className="text-xs text-slate-500 mt-1">Forensic determination across all cases</p>
          </div>

          <div className="h-56 my-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: any, name: any) => [`${value} cases`, name]}
                  contentStyle={{ backgroundColor: '#0F172A', color: '#FFF', borderRadius: '6px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100 text-xs">
            {chartData.map((d) => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                  <span className="text-slate-600">{d.name}</span>
                </div>
                <span className="font-mono font-medium text-slate-900">{d.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Distributed Systems Summary */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h3 className="text-base font-semibold text-slate-900">Discovered Systems & Critical Failure Modes</h3>
              <p className="text-xs text-slate-500 mt-1">Multi-tier datastores under automated surveillance</p>
            </div>
            <button
              onClick={() => onNavigate('systems')}
              className="text-xs text-[#B76E79] hover:text-[#8E4954] font-semibold flex items-center space-x-1"
            >
              <span>View Topology</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-[#F3E6E8] mt-2">
            {data?.systems_summary.map((sys) => (
              <div key={sys.system_id} className="py-3 flex items-center justify-between text-sm">
                <div>
                  <div className="font-semibold text-[#1E1517] font-mono text-xs">{sys.system_id}</div>
                  <div className="text-xs text-[#8C6D73] mt-0.5">{sys.name} ({sys.type})</div>
                </div>
                <div className="text-right">
                  <span className="text-xs text-[#6E575B] bg-[#FAF7F7] px-2.5 py-1 rounded border border-[#EFE4E6]">
                    {sys.risks}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Launchpad to Submission Deliverables */}
      <div className="bg-gradient-to-r from-[#1A0F12] to-[#2B181E] text-white rounded-xl p-6 flex flex-col md:flex-row items-center justify-between gap-4 shadow-sm border border-[#44232C]">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <FileCheck className="w-5 h-5 text-[#E2A6AF]" />
            <h4 className="font-bold text-base text-white">Challenge Submission Deliverables</h4>
          </div>
          <p className="text-xs text-[#D8B4BA]">
            output.csv (518 rows) | code.zip | evaluation_report.md | usage_report.md
          </p>
        </div>
        <button
          onClick={() => onNavigate('submission')}
          className="px-4 py-2 text-sm font-semibold bg-gradient-to-r from-[#B76E79] to-[#9E5762] hover:from-[#A85E69] hover:to-[#8E4954] text-white rounded-lg transition shadow-sm"
        >
          Open Submission Center
        </button>
      </div>
    </div>
  );
};
