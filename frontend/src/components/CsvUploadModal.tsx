import React, { useState, useRef } from 'react';
import {
  X,
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  Download,
  RefreshCw,
  ExternalLink,
  HelpCircle,
  FileText
} from 'lucide-react';
import {
  uploadAndAuditCsv,
  getUploadedBatchDownloadUrl,
  getSampleTemplateCsvUrl,
  UploadBatchResponse
} from '../services/api';
import { StatusBadge } from './StatusBadge';

interface CsvUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectCase: (caseId: string) => void;
}

export const CsvUploadModal: React.FC<CsvUploadModalProps> = ({ isOpen, onClose, onSelectCase }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [batchResult, setBatchResult] = useState<UploadBatchResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const selected = e.dataTransfer.files[0];
      if (selected.name.endsWith('.csv')) {
        setFile(selected);
        setError(null);
      } else {
        setError('Please drop a valid .csv file.');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0];
      if (selected.name.endsWith('.csv')) {
        setFile(selected);
        setError(null);
      } else {
        setError('Please select a valid .csv file.');
      }
    }
  };

  const handleUploadAndAudit = async () => {
    if (!file) {
      setError('Please select a .csv file first.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await uploadAndAuditCsv(file);
      setBatchResult(res);
    } catch (err: any) {
      setError(err.message || 'Audit execution failed on uploaded CSV.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setBatchResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in duration-150">
        {/* Header */}
        <div className="p-5 border-b border-[#EFE4E6] flex items-center justify-between bg-[#FDF8F9]">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-gradient-to-br from-[#B76E79] to-[#934954] rounded-lg text-white shadow-xs">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-[#1E1517] text-base">Upload & Audit Custom CSV Dataset</h3>
              <p className="text-xs text-[#8C6D73] mt-0.5">
                Ingest arbitrary customer deletion requests and execute forensic audit in real-time
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-[#A89296] hover:text-[#1E1517] hover:bg-[#F4DEE2] transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Area */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {error && (
            <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!batchResult ? (
            /* Upload Screen */
            <div className="space-y-6">
              {/* Drag and Drop Zone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition text-center ${
                  isDragging
                    ? 'border-[#B76E79] bg-[#FAF0F2]'
                    : 'border-[#E0D2D5] hover:border-[#B76E79] bg-[#FAF7F7]/60'
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".csv"
                  className="hidden"
                />
                <div className="p-4 bg-white rounded-full shadow-sm text-[#B76E79] border border-[#EAC5CB] mb-3">
                  <UploadCloud className="w-8 h-8" />
                </div>
                {file ? (
                  <div className="space-y-1">
                    <p className="font-semibold text-[#1E1517] text-sm">{file.name}</p>
                    <p className="text-xs text-[#8C6D73] font-mono">
                      {(file.size / 1024).toFixed(1)} KB — Ready to audit
                    </p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <p className="font-semibold text-slate-800 text-sm">
                      Click to upload or drag & drop a .csv file
                    </p>
                    <p className="text-xs text-slate-500">
                      Supports deletion request files, customer lists, or custom test cases
                    </p>
                  </div>
                )}
              </div>

              {/* Supported Schema Guidance */}
              <div className="p-4 bg-[#FAF7F7] rounded-lg border border-[#EFE4E6] text-xs space-y-2">
                <div className="font-semibold text-[#1E1517] flex items-center justify-between">
                  <span>Supported Column Headers (Flexible & Auto-Mapped):</span>
                  <a
                    href={getSampleTemplateCsvUrl()}
                    download="ghosttrace_sample_upload_template.csv"
                    className="text-[#B76E79] hover:text-[#8E4954] font-medium flex items-center space-x-1"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download Sample Template</span>
                  </a>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px] text-[#6E575B] pt-1">
                  <div className="p-2 bg-white rounded border border-[#EFE4E6]">
                    <span className="font-bold text-[#1E1517]">case_id</span> (or id)
                  </div>
                  <div className="p-2 bg-white rounded border border-[#EFE4E6]">
                    <span className="font-bold text-[#1E1517]">customer_id</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-[#EFE4E6]">
                    <span className="font-bold text-[#1E1517]">requested_email</span> (or email)
                  </div>
                  <div className="p-2 bg-white rounded border border-[#EFE4E6]">
                    <span className="font-bold text-[#1E1517]">request_type</span> (DELETION)
                  </div>
                  <div className="p-2 bg-white rounded border border-[#EFE4E6]">
                    <span className="font-bold text-[#1E1517]">reported_status</span> (COMPLETE)
                  </div>
                  <div className="p-2 bg-white rounded border border-[#EFE4E6]">
                    <span className="font-bold text-[#1E1517]">requested_at</span> (ISO date)
                  </div>
                  <div className="p-2 bg-white rounded border border-[#EFE4E6]">
                    <span className="font-bold text-[#1E1517]">audit_at</span> (Cutoff date)
                  </div>
                  <div className="p-2 bg-white rounded border border-[#EFE4E6] text-[#A89296] italic">
                    Auto-defaults missing
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Results Screen */
            <div className="space-y-6">
              {/* Batch KPI Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="bg-[#FAF7F7] p-3.5 rounded-lg border border-[#EFE4E6] text-center">
                  <div className="text-[10px] text-[#8C6D73] uppercase font-semibold">Total Audited</div>
                  <div className="text-2xl font-bold text-[#1E1517] font-mono mt-0.5">{batchResult.total_cases}</div>
                </div>
                <div className="bg-[#F2FAF6] p-3.5 rounded-lg border border-[#C2ECD8] text-center">
                  <div className="text-[10px] text-[#0D6847] uppercase font-semibold">Complete</div>
                  <div className="text-2xl font-bold text-[#0D6847] font-mono mt-0.5">{batchResult.complete_count}</div>
                </div>
                <div className="bg-[#FDF3F4] p-3.5 rounded-lg border border-[#F5CAD0] text-center">
                  <div className="text-[10px] text-[#A82A3A] uppercase font-semibold">Ghost Data</div>
                  <div className="text-2xl font-bold text-[#A82A3A] font-mono mt-0.5">{batchResult.incomplete_count}</div>
                </div>
                <div className="bg-[#FAF7F7] p-3.5 rounded-lg border border-[#EFE4E6] text-center">
                  <div className="text-[10px] text-[#8C6D73] uppercase font-semibold">Not Applicable</div>
                  <div className="text-2xl font-bold text-[#6E575B] font-mono mt-0.5">{batchResult.not_applicable_count}</div>
                </div>
                <div className="bg-[#FDF8F0] p-3.5 rounded-lg border border-[#F7E2BF] text-center">
                  <div className="text-[10px] text-[#9A5D15] uppercase font-semibold">Discrepancies</div>
                  <div className="text-2xl font-bold text-[#9A5D15] font-mono mt-0.5">{batchResult.discrepancy_count}</div>
                </div>
              </div>

              {/* Action Banner to Download output.csv */}
              <div className="p-4 bg-gradient-to-r from-[#1E1114] to-[#2D1A20] text-white rounded-lg flex flex-col sm:flex-row items-center justify-between gap-3 shadow-sm border border-[#482830]">
                <div className="flex items-center space-x-2.5">
                  <CheckCircle2 className="w-5 h-5 text-[#E2A6AF]" />
                  <div>
                    <div className="text-xs font-semibold text-white">Batch Audit Completed & Verified</div>
                    <div className="text-[11px] text-[#C59B9F]">Strict 3-column output CSV generated for this file</div>
                  </div>
                </div>
                <a
                  href={getUploadedBatchDownloadUrl(batchResult.batch_id)}
                  download={`audited_output_${batchResult.batch_id}.csv`}
                  className="px-4 py-1.5 text-xs font-semibold bg-gradient-to-r from-[#B76E79] to-[#9E5762] hover:from-[#A85E69] hover:to-[#8E4954] text-white rounded-lg flex items-center space-x-1.5 transition shadow-sm"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download output.csv</span>
                </a>
              </div>

              {/* Cases Table */}
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <div className="p-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-700 flex items-center justify-between">
                  <span>Audited Cases from {batchResult.filename}</span>
                  <span className="text-slate-400 font-normal">Click any case row to investigate forensic evidence</span>
                </div>
                <div className="max-h-72 overflow-y-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-600 uppercase sticky top-0">
                      <tr>
                        <th className="px-4 py-2.5">Case ID</th>
                        <th className="px-4 py-2.5">Requested Email</th>
                        <th className="px-4 py-2.5">Reported</th>
                        <th className="px-4 py-2.5">Audited Deletion Status</th>
                        <th className="px-4 py-2.5 text-center">Findings</th>
                        <th className="px-4 py-2.5 text-center">Remediation</th>
                        <th className="px-4 py-2.5 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono">
                      {batchResult.cases.map((c) => (
                        <tr
                          key={c.case_id}
                          onClick={() => {
                            onClose();
                            onSelectCase(c.case_id);
                          }}
                          className="hover:bg-slate-50/80 cursor-pointer transition"
                        >
                          <td className="px-4 py-2.5 font-bold text-slate-900">{c.case_id}</td>
                          <td className="px-4 py-2.5 text-slate-600">{c.requested_email}</td>
                          <td className="px-4 py-2.5 font-sans">
                            <StatusBadge status={c.reported_status} type="reported" size="sm" />
                          </td>
                          <td className="px-4 py-2.5 font-sans">
                            <div className="flex items-center space-x-1.5">
                              <StatusBadge status={c.deletion_status} type="deletion" size="sm" />
                              {c.has_discrepancy && (
                                <span className="px-1.5 py-0.5 rounded text-[9px] bg-rose-100 text-rose-700 font-semibold">
                                  Ghost Data
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-2.5 text-center font-bold text-slate-700">{c.findings_count}</td>
                          <td className="px-4 py-2.5 text-center font-bold text-slate-700">{c.remediation_count}</td>
                          <td className="px-4 py-2.5 text-right font-sans">
                            <button className="text-[#B76E79] hover:text-[#8E4954] text-xs font-semibold">
                              Investigate &rarr;
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#EFE4E6] bg-[#FAF7F7] flex items-center justify-between">
          {!batchResult ? (
            <div className="text-xs text-[#8C6D73]">
              {file ? `Selected file: ${file.name}` : 'No file chosen.'}
            </div>
          ) : (
            <button
              onClick={handleReset}
              className="px-3.5 py-1.5 text-xs font-medium text-[#4A2027] bg-white border border-[#EAC5CB] rounded-lg hover:bg-[#FAF0F2] transition"
            >
              Upload Another CSV
            </button>
          )}

          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-[#6E575B] hover:text-[#1E1517] hover:bg-[#F3E6E8] rounded-lg transition"
            >
              {batchResult ? 'Close' : 'Cancel'}
            </button>
            {!batchResult && (
              <button
                onClick={handleUploadAndAudit}
                disabled={!file || loading}
                className="px-5 py-2 text-xs font-semibold text-white bg-gradient-to-r from-[#B76E79] to-[#9E5762] hover:from-[#A85E69] hover:to-[#8E4954] disabled:opacity-50 rounded-lg transition flex items-center space-x-2 shadow-sm"
              >
                {loading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                <span>{loading ? 'Forensic Audit in Progress...' : 'Audit Uploaded CSV'}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
