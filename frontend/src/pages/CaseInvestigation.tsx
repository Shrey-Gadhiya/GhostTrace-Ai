import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  Clock,
  UserCheck,
  FileSearch,
  CheckCircle2,
  Copy,
  Check,
  FileCode,
  AlertTriangle,
  RefreshCw,
  Hash,
  Database
} from 'lucide-react';
import { fetchCaseDetail, fetchCaseEvidence, CaseDetail, CaseEvidenceResponse } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

interface CaseInvestigationProps {
  caseId: string;
  onBack: () => void;
}

export const CaseInvestigation: React.FC<CaseInvestigationProps> = ({ caseId, onBack }) => {
  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [evidenceData, setEvidenceData] = useState<CaseEvidenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'summary' | 'identities' | 'evidence' | 'findings' | 'remediation' | 'verification' | 'raw'>('summary');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [det, ev] = await Promise.all([
          fetchCaseDetail(caseId),
          fetchCaseEvidence(caseId)
        ]);
        setDetail(det);
        setEvidenceData(ev);
      } catch (err: any) {
        console.error('Failed to load case detail:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [caseId]);

  const handleCopyRaw = () => {
    if (detail?.steps_json) {
      navigator.clipboard.writeText(detail.steps_json);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw className="w-6 h-6 animate-spin text-[#B76E79]" />
          <span className="text-sm text-slate-500 font-medium">Loading forensic dossier for {caseId}...</span>
        </div>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="p-8 text-center text-slate-500">
        <p>Case not found.</p>
        <button onClick={onBack} className="mt-4 px-4 py-2 text-sm bg-slate-100 rounded">
          Back to Case Explorer
        </button>
      </div>
    );
  }

  const isDiscrepancy =
    detail.reported_status === 'COMPLETE' && detail.deletion_status === 'INCOMPLETE';

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Back button */}
      <button
        onClick={onBack}
        className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Case Explorer</span>
      </button>

      {/* Case Header Card */}
      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-slate-900 rounded-lg text-white">
              <FileSearch className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-xl font-bold text-slate-900 font-mono tracking-tight">{detail.case_id}</h2>
                <span className="text-xs font-mono text-slate-500">({detail.customer_id})</span>
              </div>
              <p className="text-xs text-slate-500 font-mono mt-0.5">{detail.requested_email}</p>
            </div>
          </div>

          {/* Status Badges Header */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Reported Workflow</div>
              <div className="mt-0.5">
                <StatusBadge status={detail.reported_status} type="reported" size="sm" />
              </div>
            </div>

            <div className="h-8 w-px bg-slate-200 mx-1" />

            <div className="text-right">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Audited Status</div>
              <div className="mt-0.5">
                <StatusBadge status={detail.deletion_status} type="deletion" size="md" />
              </div>
            </div>
          </div>
        </div>

        {/* Timestamps and Discrepancy Alert */}
        <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center space-x-6">
            <div>
              <span className="text-slate-400">Requested: </span>
              <span className="font-mono text-slate-700">{detail.requested_at}</span>
            </div>
            <div>
              <span className="text-slate-400">Audit Cutoff (audit_at): </span>
              <span className="font-mono text-slate-700">{detail.audit_at}</span>
            </div>
            <div>
              <span className="text-slate-400">Request Type: </span>
              <span className="font-semibold text-slate-800">{detail.request_type}</span>
            </div>
          </div>

          {isDiscrepancy && (
            <div className="px-2.5 py-1 bg-rose-50 border border-rose-200 text-rose-800 rounded text-xs flex items-center space-x-1.5 font-medium">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
              <span>Ghost Data Discrepancy: Primary system claimed COMPLETE but evidence proves residual records linger.</span>
            </div>
          )}
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-slate-200 flex space-x-1">
        {[
          { id: 'summary', label: '1. Summary' },
          { id: 'identities', label: `2. Identity History (${detail.identities.length})` },
          { id: 'evidence', label: `3. Evidence (${evidenceData?.evidence.length || 0})` },
          { id: 'findings', label: `4. Findings (${detail.findings.length})` },
          { id: 'remediation', label: `5. Remediation Plan (${detail.remediations.length})` },
          { id: 'verification', label: `6. Verification (${detail.verifications.length})` },
          { id: 'raw', label: '7. Raw steps_json' }
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as any)}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === t.id
                ? 'border-[#B76E79] text-[#89434E] bg-white font-bold'
                : 'border-transparent text-[#8C6D73] hover:text-[#1E1517]'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Summary */}
      {activeTab === 'summary' && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Executive Audit Determination</h3>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded border border-slate-200 font-sans">
            {detail.summary}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
            <div className="p-4 bg-slate-50 rounded border border-slate-200">
              <div className="text-xs text-slate-500 font-medium">Unresolved Findings</div>
              <div className="text-2xl font-bold text-slate-900 font-mono mt-1">{detail.findings.length}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Policy violations discovered</div>
            </div>
            <div className="p-4 bg-slate-50 rounded border border-slate-200">
              <div className="text-xs text-slate-500 font-medium">Required Remediation Actions</div>
              <div className="text-2xl font-bold text-slate-900 font-mono mt-1">{detail.remediations.length}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Purge, redact, or block steps</div>
            </div>
            <div className="p-4 bg-slate-50 rounded border border-slate-200">
              <div className="text-xs text-slate-500 font-medium">Target Verification Checks</div>
              <div className="text-2xl font-bold text-slate-900 font-mono mt-1">{detail.verifications.length}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Post-remediation verification</div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Identity History */}
      {activeTab === 'identities' && (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 text-xs text-slate-500">
            Resolved master and linked identity values across distributed systems. Transitive merging of unverified links is prohibited.
          </div>
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-600 uppercase">
              <tr>
                <th className="px-5 py-3">Identifier Value</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Source System</th>
                <th className="px-5 py-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {detail.identities.map((id, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="px-5 py-3 font-semibold text-slate-900">{id.identifier_value}</td>
                  <td className="px-5 py-3 text-slate-600">{id.identifier_type}</td>
                  <td className="px-5 py-3">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                      {id.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-600">{id.source_system}</td>
                  <td className="px-5 py-3">
                    <span
                      className={`px-2 py-0.5 rounded font-semibold ${
                        id.confidence === 'CONFIRMED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}
                    >
                      {id.confidence}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Evidence */}
      {activeTab === 'evidence' && (
        <div className="space-y-4">
          {evidenceData && evidenceData.evidence.length > 0 ? (
            evidenceData.evidence.map((ev) => (
              <div key={ev.evidence_id} className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 bg-[#FAF2F3] text-[#8C4F5A] border border-[#E8D7D8] rounded font-mono font-bold text-xs">
                      {ev.evidence_id}
                    </span>
                    <span className="font-mono text-xs font-semibold text-slate-800">{ev.system_id}</span>
                    <span className="text-slate-400 text-xs">&rarr;</span>
                    <span className="font-mono text-xs text-slate-600">{ev.resource_id}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded font-mono text-[11px]">
                      {ev.file_type}
                    </span>
                    {ev.is_valid_hash && (
                      <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-[11px] font-medium flex items-center space-x-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>SHA-256 Verified</span>
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-600">{ev.description}</p>

                {/* Snippet Viewer */}
                <div className="bg-slate-900 rounded p-3 text-slate-200 font-mono text-xs overflow-x-auto max-h-48">
                  <pre className="whitespace-pre-wrap">{ev.snippet}</pre>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>Path: {ev.file_path}</span>
                  <span>Collected at: {ev.collected_at}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-slate-400 bg-white rounded-lg border border-slate-200">
              No evidence files registered for this case.
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Findings */}
      {activeTab === 'findings' && (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
          {detail.findings.length > 0 ? (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-600 uppercase">
                <tr>
                  <th className="px-5 py-3">Step #</th>
                  <th className="px-5 py-3">System</th>
                  <th className="px-5 py-3">Resource</th>
                  <th className="px-5 py-3">Operation</th>
                  <th className="px-5 py-3">State</th>
                  <th className="px-5 py-3">Evidence ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {detail.findings.map((f) => (
                  <tr key={f.step_no} className="hover:bg-rose-50/30">
                    <td className="px-5 py-3 font-semibold text-slate-900">{f.step_no}</td>
                    <td className="px-5 py-3 text-slate-700">{f.system_id}</td>
                    <td className="px-5 py-3 text-[#554E52]">{f.resource_id}</td>
                    <td className="px-5 py-3 font-semibold text-rose-700">{f.operation}</td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800">{f.state}</span>
                    </td>
                    <td className="px-5 py-3 text-[#B76E79] font-semibold">{f.evidence_id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-400">
              Zero findings recorded. All applicable resources satisfied deletion policy.
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Remediation */}
      {activeTab === 'remediation' && (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
          {detail.remediations.length > 0 ? (
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAF7F7] border-b border-[#EFE4E6] font-semibold text-[#8C6D73] uppercase">
                <tr>
                  <th className="px-5 py-3">Step #</th>
                  <th className="px-5 py-3">System</th>
                  <th className="px-5 py-3">Resource</th>
                  <th className="px-5 py-3">Operation</th>
                  <th className="px-5 py-3">Target State</th>
                  <th className="px-5 py-3">Evidence ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {detail.remediations.map((r) => (
                  <tr key={r.step_no} className="hover:bg-[#FAF0F2]/40">
                    <td className="px-5 py-3 font-semibold text-slate-900">{r.step_no}</td>
                    <td className="px-5 py-3 text-slate-700">{r.system_id}</td>
                    <td className="px-5 py-3 text-slate-600">{r.resource_id}</td>
                    <td className="px-5 py-3 font-semibold text-[#89434E]">{r.operation}</td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-0.5 rounded bg-[#FAF0F2] text-[#89434E] font-medium border border-[#EAC5CB]">{r.state}</span>
                    </td>
                    <td className="px-5 py-3 text-slate-400 font-mono italic">"" (proposed)</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-400">
              No remediation actions required.
            </div>
          )}
        </div>
      )}

      {/* Tab 6: Verification */}
      {activeTab === 'verification' && (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
          {detail.verifications.length > 0 ? (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-600 uppercase">
                <tr>
                  <th className="px-5 py-3">Step #</th>
                  <th className="px-5 py-3">System</th>
                  <th className="px-5 py-3">Resource</th>
                  <th className="px-5 py-3">Operation</th>
                  <th className="px-5 py-3">State</th>
                  <th className="px-5 py-3">Evidence ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {detail.verifications.map((v) => (
                  <tr key={v.step_no} className="hover:bg-emerald-50/30">
                    <td className="px-5 py-3 font-semibold text-slate-900">{v.step_no}</td>
                    <td className="px-5 py-3 text-slate-700">{v.system_id}</td>
                    <td className="px-5 py-3 text-slate-600">{v.resource_id}</td>
                    <td className="px-5 py-3 font-semibold text-emerald-700">{v.operation}</td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">{v.state}</span>
                    </td>
                    <td className="px-5 py-3 text-[#B76E79] font-semibold">
                      {v.evidence_id ? v.evidence_id : <span className="text-slate-400 italic">"" (future check)</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-400">
              No verification steps recorded.
            </div>
          )}
        </div>
      )}

      {/* Tab 7: Raw JSON */}
      {activeTab === 'raw' && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Serialized steps_json output</h3>
              <p className="text-xs text-slate-500 mt-0.5">Strict array for output.csv row serialization</p>
            </div>
            <button
              onClick={handleCopyRaw}
              className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 flex items-center space-x-1.5 shadow-sm"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied to clipboard' : 'Copy JSON'}</span>
            </button>
          </div>

          <div className="bg-slate-950 p-4 rounded-lg text-slate-200 font-mono text-xs overflow-x-auto max-h-96">
            <pre>{JSON.stringify(JSON.parse(detail.steps_json || '[]'), null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};
