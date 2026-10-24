import React, { useState, useEffect } from 'react';
import {
  Network,
  Database,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Shield,
  Layers,
  ArrowRight,
  ExternalLink
} from 'lucide-react';
import { fetchSystems } from '../services/api';

export const SystemsFlows: React.FC = () => {
  const [systems, setSystems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSystem, setSelectedSystem] = useState<any | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetchSystems();
        setSystems(res.systems || []);
        if (res.systems?.length > 0) {
          setSelectedSystem(res.systems[0]);
        }
      } catch (err: any) {
        console.error('Failed to load systems:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-[#B76E79]" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Systems & Distributed Data Flows</h2>
        <p className="text-sm text-slate-500 mt-1">
          Forensic surveillance across Northstar Shop multi-tier storage and integration streams
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Systems List */}
        <div className="space-y-3">
          {systems.map((s) => {
            const isSelected = selectedSystem?.system_id === s.system_id;
            return (
              <div
                key={s.system_id}
                onClick={() => setSelectedSystem(s)}
                className={`p-4 rounded-xl border transition cursor-pointer ${
                  isSelected
                    ? 'bg-white border-[#B76E79] shadow-md ring-1 ring-[#B76E79]'
                    : 'bg-white border-[#EFE4E6] hover:border-[#D8B7BC] shadow-xs'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-slate-900">{s.system_id}</span>
                  <div className="flex items-center space-x-1.5">
                    {s.has_active_data_flow && (
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-100 text-rose-800">
                        Active Flow
                      </span>
                    )}
                    {s.has_restore_risk && (
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800">
                        Restore Risk
                      </span>
                    )}
                  </div>
                </div>

                <div className="text-sm font-semibold text-slate-800 mt-1">{s.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">{s.category}</div>

                <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>{s.evidence_count} evidence records</span>
                  <span>{s.environment}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected System Rules & Forensics Details */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-[#EFE4E6] shadow-xs space-y-6">
          {selectedSystem ? (
            <>
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono font-bold text-[#89434E] bg-[#FAF0F2] px-2.5 py-1 rounded border border-[#EAC5CB]">
                      {selectedSystem.system_id}
                    </span>
                    <h3 className="text-lg font-bold text-slate-900">{selectedSystem.name}</h3>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Environment: {selectedSystem.environment} | Storage: {selectedSystem.storage_type}
                  </p>
                </div>
              </div>

              {/* Data Flow & Hazard Warnings */}
              {selectedSystem.has_active_data_flow && (
                <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 space-y-1">
                  <div className="font-semibold flex items-center space-x-1.5">
                    <AlertTriangle className="w-4 h-4 text-rose-600" />
                    <span>Active Replication Pipeline Detected</span>
                  </div>
                  <p>
                    Automated background sync worker jobs run periodically. Policy mandates executing <code>DISABLE_DATA_FLOW</code> before certifying erasure.
                  </p>
                </div>
              )}

              {selectedSystem.has_restore_risk && (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 space-y-1">
                  <div className="font-semibold flex items-center space-x-1.5">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>Point-in-Time Restore Hazard</span>
                  </div>
                  <p>
                    Cold backup tarballs or snapshots in S3 Glacier can restore deleted customer data. Policy mandates executing <code>BLOCK_RESTORE</code>.
                  </p>
                </div>
              )}

              {/* Authoritative Deletion Policies for this System */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Authoritative Deletion Rules (deletion_rules.csv)
                </h4>
                {selectedSystem.rules && selectedSystem.rules.length > 0 ? (
                  <div className="space-y-3">
                    {selectedSystem.rules.map((rule: any) => (
                      <div key={rule.rule_id} className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-2 font-sans">
                        <div className="flex items-center justify-between font-mono">
                          <span className="font-bold text-slate-900">{rule.rule_id}</span>
                          <span className={`px-2 py-0.5 rounded font-bold ${
                            rule.required_treatment === 'DELETE' ? 'bg-rose-100 text-rose-800' :
                            rule.required_treatment === 'REDACT' ? 'bg-[#FAF0F2] text-[#89434E] border border-[#EAC5CB]' :
                            rule.required_treatment === 'RETAIN' ? 'bg-emerald-100 text-emerald-800' :
                            'bg-purple-100 text-purple-800'
                          }`}>
                            REQUIRED: {rule.required_treatment}
                          </span>
                        </div>
                        <div className="text-slate-700 font-medium">{rule.retention_rationale}</div>
                        
                        {rule.prohibited_fields && (
                          <div className="text-slate-600 font-mono text-[11px]">
                            <span className="font-semibold text-rose-700">Prohibited Direct PII: </span>
                            {rule.prohibited_fields}
                          </div>
                        )}
                        {rule.allowed_fields && (
                          <div className="text-slate-600 font-mono text-[11px]">
                            <span className="font-semibold text-emerald-700">Allowed Retained Fields: </span>
                            {rule.allowed_fields}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">No system-specific rules. Governed by global wildcard policy.</p>
                )}
              </div>
            </>
          ) : (
            <div className="p-8 text-center text-slate-400">Select a system to inspect details.</div>
          )}
        </div>
      </div>
    </div>
  );
};
