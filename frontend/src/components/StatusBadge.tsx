import React from 'react';
import { CheckCircle2, AlertCircle, MinusCircle, Clock, ShieldCheck } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  type?: 'deletion' | 'reported' | 'phase' | 'state';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'deletion', size = 'md' }) => {
  const norm = (status || '').toUpperCase();
  const textClass = size === 'sm' ? 'text-[11px] px-2 py-0.5' : 'text-xs px-2.5 py-1';

  if (type === 'deletion') {
    switch (norm) {
      case 'COMPLETE':
        return (
          <span className={`inline-flex items-center space-x-1 rounded-full font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 ${textClass}`}>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>COMPLETE</span>
          </span>
        );
      case 'INCOMPLETE':
        return (
          <span className={`inline-flex items-center space-x-1 rounded-full font-medium bg-rose-50 text-rose-700 border border-rose-200 ${textClass}`}>
            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>INCOMPLETE</span>
          </span>
        );
      case 'NOT_APPLICABLE':
        return (
          <span className={`inline-flex items-center space-x-1 rounded-full font-medium bg-slate-100 text-slate-700 border border-slate-300 ${textClass}`}>
            <MinusCircle className="w-3.5 h-3.5 text-slate-500" />
            <span>NOT_APPLICABLE</span>
          </span>
        );
      default:
        return (
          <span className={`inline-flex items-center rounded-full font-medium bg-slate-100 text-slate-600 border border-slate-200 ${textClass}`}>
            {status}
          </span>
        );
    }
  }

  if (type === 'reported') {
    switch (norm) {
      case 'COMPLETE':
        return (
          <span className={`inline-flex items-center space-x-1 rounded font-mono font-medium bg-slate-100 text-slate-700 border border-slate-200 ${textClass}`}>
            <span>{status}</span>
          </span>
        );
      case 'IN_PROGRESS':
      case 'PENDING':
        return (
          <span className={`inline-flex items-center space-x-1 rounded font-mono font-medium bg-amber-50 text-amber-800 border border-amber-200 ${textClass}`}>
            <Clock className="w-3 h-3 text-amber-600" />
            <span>{status}</span>
          </span>
        );
      default:
        return (
          <span className={`inline-flex items-center rounded font-mono font-medium bg-slate-100 text-slate-600 border border-slate-200 ${textClass}`}>
            {status}
          </span>
        );
    }
  }

  if (type === 'phase') {
    switch (norm) {
      case 'FINDINGS':
        return (
          <span className={`inline-flex items-center rounded font-mono font-semibold bg-rose-100 text-rose-800 border border-rose-200 ${textClass}`}>
            FINDINGS
          </span>
        );
      case 'REMEDIATION':
        return (
          <span className={`inline-flex items-center rounded font-mono font-semibold bg-[#FAF0F2] text-[#89434E] border border-[#EAC5CB] ${textClass}`}>
            REMEDIATION
          </span>
        );
      case 'VERIFICATION':
        return (
          <span className={`inline-flex items-center rounded font-mono font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 ${textClass}`}>
            VERIFICATION
          </span>
        );
      default:
        return <span>{status}</span>;
    }
  }

  // State badge
  return (
    <span className={`inline-flex items-center rounded font-mono font-medium bg-slate-100 text-slate-800 border border-slate-200 ${textClass}`}>
      {status}
    </span>
  );
};
