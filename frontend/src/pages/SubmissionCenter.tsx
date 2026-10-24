import React, { useState, useEffect } from 'react';
import {
  FileArchive,
  Download,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileSpreadsheet,
  FileText,
  Package,
  RefreshCw,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import {
  fetchSubmissionStatus,
  exportOutputCsv,
  createSubmissionZip
} from '../services/api';

export const SubmissionCenter: React.FC = () => {
  const [status, setStatus] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingCsv, setGeneratingCsv] = useState(false);
  const [generatingZip, setGeneratingZip] = useState(false);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const res = await fetchSubmissionStatus();
      setStatus(res);
    } catch (err: any) {
      console.error('Failed to load submission status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleExportCsv = async () => {
    try {
      setGeneratingCsv(true);
      await exportOutputCsv();
      await loadStatus();
    } catch (err: any) {
      alert('Error exporting CSV: ' + err.message);
    } finally {
      setGeneratingCsv(false);
    }
  };

  const handleCreateZip = async () => {
    try {
      setGeneratingZip(true);
      await createSubmissionZip();
      await loadStatus();
    } catch (err: any) {
      alert('Error creating ZIP: ' + err.message);
    } finally {
      setGeneratingZip(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-[#B76E79]" />
      </div>
    );
  }

  const arts = status?.artifacts || {};

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[#EFE4E6]">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Challenge Submission Center</h2>
          <p className="text-sm text-slate-500 mt-1">
            HackerRank Orchestrate October 2026: "Ghost Data Still Exists" Deliverables Packaging
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={loadStatus}
            className="px-3.5 py-1.5 text-xs font-semibold text-[#6E575B] bg-white border border-[#E0D2D5] rounded-lg hover:bg-[#FAF0F2] flex items-center space-x-1.5 shadow-xs"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[#8C6D73]" />
            <span>Verify All Files</span>
          </button>
        </div>
      </div>

      {/* Readiness Banner */}
      <div className={`p-5 rounded-xl border flex items-center justify-between ${
        status?.all_ready
          ? 'bg-[#F2FAF6] border-[#C2ECD8] text-[#0D6847]'
          : 'bg-[#FDF8F0] border-[#F7E2BF] text-[#9A5D15]'
      }`}>
        <div className="flex items-center space-x-3">
          {status?.all_ready ? (
            <CheckCircle2 className="w-6 h-6 text-[#10B981] shrink-0" />
          ) : (
            <AlertTriangle className="w-6 h-6 text-[#D97706] shrink-0" />
          )}
          <div>
            <h3 className="font-bold text-sm">
              {status?.all_ready
                ? 'All Submission Deliverables Verified & Ready'
                : 'Action Required: Generate Outstanding Submission Artifacts'}
            </h3>
            <p className="text-xs mt-0.5 opacity-90">
              {status?.all_ready
                ? 'output.csv (518 rows), code.zip, evaluation report, and usage report have been generated and validated.'
                : 'Please use the action buttons below to compile and serialize the final submission bundle.'}
            </p>
          </div>
        </div>
      </div>

      {/* Deliverables Checklist Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Artifact 1: output.csv */}
        <div className="bg-white p-6 rounded-xl border border-[#EFE4E6] shadow-xs space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-[#FAF0F2] text-[#89434E] border border-[#EAC5CB] rounded-lg">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm font-mono">output.csv</h4>
                <p className="text-xs text-slate-500">Authoritative 3-column challenge result file</p>
              </div>
            </div>
            {arts.output_csv?.is_ready ? (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                READY (518/518)
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-100 text-rose-800">
                NOT READY
              </span>
            )}
          </div>

          <div className="text-xs text-slate-600 space-y-1 font-mono bg-slate-50 p-3 rounded">
            <div>Columns: case_id, deletion_status, steps_json</div>
            <div>Row Count: {arts.output_csv?.row_count} / {arts.output_csv?.expected_rows}</div>
            <div>Schema: Strict JSON Array, 15 Authoritative Operations</div>
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <button
              onClick={handleExportCsv}
              disabled={generatingCsv}
              className="px-3.5 py-1.5 text-xs font-medium text-white bg-slate-900 rounded hover:bg-slate-800 disabled:opacity-50 transition"
            >
              {generatingCsv ? 'Generating...' : 'Re-Generate output.csv'}
            </button>
            {arts.output_csv?.exists && (
              <a
                href="/api/downloads/output-csv"
                download="output.csv"
                className="px-3.5 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 flex items-center space-x-1"
              >
                <Download className="w-3.5 h-3.5 text-slate-500" />
                <span>Download output.csv</span>
              </a>
            )}
          </div>
        </div>

        {/* Artifact 2: code.zip */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-purple-50 text-purple-700 rounded-lg">
                <Package className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm font-mono">code.zip</h4>
                <p className="text-xs text-slate-500">Complete runnable codebase without secrets</p>
              </div>
            </div>
            {arts.code_zip?.is_ready ? (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                READY ({Math.round(arts.code_zip?.size_bytes / 1024)} KB)
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-600">
                AWAITING PACK
              </span>
            )}
          </div>

          <div className="text-xs text-slate-600 space-y-1 font-mono bg-slate-50 p-3 rounded">
            <div>Includes: Backend, Frontend, Prompts, Tests, Docs</div>
            <div>Excludes: node_modules, .venv, .git, real secrets</div>
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <button
              onClick={handleCreateZip}
              disabled={generatingZip}
              className="px-3.5 py-1.5 text-xs font-medium text-white bg-slate-900 rounded hover:bg-slate-800 disabled:opacity-50 transition"
            >
              {generatingZip ? 'Packaging...' : 'Build code.zip'}
            </button>
            {arts.code_zip?.exists && (
              <a
                href="/api/downloads/code-zip"
                download="code.zip"
                className="px-3.5 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 flex items-center space-x-1"
              >
                <Download className="w-3.5 h-3.5 text-slate-500" />
                <span>Download code.zip</span>
              </a>
            )}
          </div>
        </div>

        {/* Artifact 3: evaluation_report.md */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-emerald-50 text-emerald-700 rounded-lg">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm font-mono">evaluation/evaluation_report.md</h4>
                <p className="text-xs text-slate-500">Forensic evaluation report with benchmark metrics</p>
              </div>
            </div>
            {arts.evaluation_report?.is_ready ? (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                READY
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-100 text-rose-800">
                PENDING
              </span>
            )}
          </div>

          <div className="text-xs text-slate-600 space-y-1 font-mono bg-slate-50 p-3 rounded">
            <div>Scope: Status, step, field, sequence accuracy metrics</div>
            <div>Contains: 3 Team-Authored Edge Cases + Sample comparisons</div>
          </div>

          <div className="pt-2">
            {arts.evaluation_report?.exists && (
              <a
                href="/api/downloads/evaluation-report"
                download="evaluation_report.md"
                className="px-3.5 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 inline-flex items-center space-x-1"
              >
                <Download className="w-3.5 h-3.5 text-slate-500" />
                <span>Download evaluation_report.md</span>
              </a>
            )}
          </div>
        </div>

        {/* Artifact 4: usage_report.md */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-amber-50 text-amber-700 rounded-lg">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm font-mono">evaluation/usage_report.md</h4>
                <p className="text-xs text-slate-500">LLM token usage, call count, and cost accounting</p>
              </div>
            </div>
            {arts.usage_report?.is_ready ? (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                READY
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-100 text-rose-800">
                PENDING
              </span>
            )}
          </div>

          <div className="text-xs text-slate-600 space-y-1 font-mono bg-slate-50 p-3 rounded">
            <div>Scope: Prompt/completion tokens, pricing rates, model IDs</div>
            <div>Policy: Deterministic-first fallback with full transparency</div>
          </div>

          <div className="pt-2">
            {arts.usage_report?.exists && (
              <a
                href="/api/downloads/usage-report"
                download="usage_report.md"
                className="px-3.5 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 inline-flex items-center space-x-1"
              >
                <Download className="w-3.5 h-3.5 text-slate-500" />
                <span>Download usage_report.md</span>
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
