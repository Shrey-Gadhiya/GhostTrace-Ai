import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ExternalLink,
  AlertTriangle,
  RefreshCw,
  FileSpreadsheet
} from 'lucide-react';
import { fetchCases, CasesResponse, CaseListItem } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

interface CaseExplorerProps {
  onSelectCase: (caseId: string) => void;
  onOpenUpload?: () => void;
}

export const CaseExplorer: React.FC<CaseExplorerProps> = ({ onSelectCase, onOpenUpload }) => {
  const [data, setData] = useState<CasesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [search, setSearch] = useState('');
  const [deletionStatus, setDeletionStatus] = useState('');
  const [reportedStatus, setReportedStatus] = useState('');

  const loadCases = async () => {
    try {
      setLoading(true);
      const res = await fetchCases({
        page,
        pageSize,
        search: search.trim() || undefined,
        deletionStatus: deletionStatus || undefined,
        reportedStatus: reportedStatus || undefined
      });
      setData(res);
    } catch (err: any) {
      console.error('Failed to load cases:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [page, pageSize, deletionStatus, reportedStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadCases();
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Page Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Case Explorer</h2>
          <p className="text-sm text-slate-500 mt-1">
            Forensic audit results across all 518 customer deletion requests
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {onOpenUpload && (
            <button
              onClick={onOpenUpload}
              className="px-3.5 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-[#B76E79] to-[#9E5762] hover:from-[#A85E69] hover:to-[#8E4954] rounded-lg transition shadow-xs flex items-center space-x-1"
            >
              <span>Upload Custom CSV</span>
            </button>
          )}
          <button
            onClick={() => {
              setSearch('');
              setDeletionStatus('');
              setReportedStatus('');
              setPage(1);
            }}
            className="px-3 py-1.5 text-xs font-medium text-[#6E575B] bg-white border border-[#E0D2D5] rounded-lg hover:bg-[#FAF0F2] transition"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-[#EFE4E6] shadow-xs flex flex-col md:flex-row gap-4 justify-between items-center">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#A89296]" />
          <input
            type="text"
            placeholder="Search by Case ID or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-sm border border-[#E0D2D5] rounded-lg focus:outline-none focus:ring-1 focus:ring-[#B76E79] focus:border-[#B76E79]"
          />
        </form>

        {/* Status Dropdowns */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span>Audited Status:</span>
            <select
              value={deletionStatus}
              onChange={(e) => {
                setDeletionStatus(e.target.value);
                setPage(1);
              }}
              className="text-xs border border-slate-300 rounded px-2 py-1 bg-white focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="COMPLETE">COMPLETE</option>
              <option value="INCOMPLETE">INCOMPLETE (Ghost Data)</option>
              <option value="NOT_APPLICABLE">NOT_APPLICABLE</option>
            </select>
          </div>

          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <span>Reported Status:</span>
            <select
              value={reportedStatus}
              onChange={(e) => {
                setReportedStatus(e.target.value);
                setPage(1);
              }}
              className="text-xs border border-slate-300 rounded px-2 py-1 bg-white focus:outline-none"
            >
              <option value="">All Reported</option>
              <option value="COMPLETE">COMPLETE</option>
              <option value="IN_PROGRESS">IN_PROGRESS</option>
              <option value="PENDING">PENDING</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-600 font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-5 py-3.5">Case ID</th>
                <th className="px-5 py-3.5">Requested Email</th>
                <th className="px-5 py-3.5">Reported Status</th>
                <th className="px-5 py-3.5">Audited Status</th>
                <th className="px-5 py-3.5 text-center">Findings</th>
                <th className="px-5 py-3.5 text-center">Remediation</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    <div className="flex items-center justify-center space-x-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-[#B76E79]" />
                      <span>Loading case records...</span>
                    </div>
                  </td>
                </tr>
              ) : data && data.items.length > 0 ? (
                data.items.map((c) => {
                  const isDiscrepancy =
                    c.reported_status === 'COMPLETE' && c.deletion_status === 'INCOMPLETE';

                  return (
                    <tr
                      key={c.case_id}
                      onClick={() => onSelectCase(c.case_id)}
                      className="hover:bg-[#FAF0F2]/50 transition-colors cursor-pointer group"
                    >
                      <td className="px-5 py-3.5 font-mono text-xs font-semibold text-[#1E1517]">
                        {c.case_id}
                      </td>
                      <td className="px-5 py-3.5 text-[#6E575B] font-mono text-xs">
                        {c.requested_email}
                      </td>
                      <td className="px-5 py-3.5">
                        <StatusBadge status={c.reported_status} type="reported" size="sm" />
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center space-x-2">
                          <StatusBadge status={c.deletion_status} type="deletion" size="sm" />
                          {isDiscrepancy && (
                            <span
                              title="Discrepancy: Reported COMPLETE by system but forensic audit discovered ghost data"
                              className="px-1.5 py-0.5 rounded text-[10px] bg-rose-100 text-rose-700 font-semibold flex items-center space-x-1"
                            >
                              <AlertTriangle className="w-3 h-3 text-rose-600" />
                              <span>Ghost Data</span>
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-center font-mono text-xs font-semibold text-[#1E1517]">
                        {c.findings_count}
                      </td>
                      <td className="px-5 py-3.5 text-center font-mono text-xs font-semibold text-[#1E1517]">
                        {c.remediation_count}
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectCase(c.case_id);
                          }}
                          className="px-2.5 py-1 text-xs font-semibold text-[#B76E79] hover:text-[#8E4954] hover:bg-[#FAF0F2] rounded-lg transition"
                        >
                          Investigate &rarr;
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No cases match the selected search or status filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {data && (
          <div className="p-4 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
            <div>
              Showing <span className="font-semibold text-slate-700">{data.items.length}</span> of{' '}
              <span className="font-semibold text-slate-700">{data.total}</span> cases
            </div>
            <div className="flex items-center space-x-3">
              <span>
                Page {data.page} of {data.total_pages}
              </span>
              <div className="flex items-center space-x-1">
                <button
                  disabled={data.page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="p-1 rounded border border-slate-300 hover:bg-slate-50 disabled:opacity-40"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={data.page >= data.total_pages}
                  onClick={() => setPage((p) => p + 1)}
                  className="p-1 rounded border border-slate-300 hover:bg-slate-50 disabled:opacity-40"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
