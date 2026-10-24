import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Shield,
  Key,
  Database,
  Cpu,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export const Settings: React.FC = () => {
  const [provider, setProvider] = useState('mock');
  const [model, setModel] = useState('gemini-1.5-flash');
  const [batchSize, setBatchSize] = useState(50);
  const [maskPiiInLogs, setMaskPiiInLogs] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Audit Platform Settings</h2>
        <p className="text-sm text-slate-500 mt-1">
          Configure runtime engine parameters, model orchestration, and privacy filters
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Dataset & Storage */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-slate-900">
            <Database className="w-4 h-4 text-[#B76E79]" />
            <span>Dataset & Local Storage</span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-600 font-medium">Dataset Directory</label>
              <input
                type="text"
                readOnly
                value="d:/orch hackthon project/dataset"
                className="mt-1 w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 font-mono text-slate-700 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-slate-600 font-medium">SQLite Application Database</label>
              <input
                type="text"
                readOnly
                value="d:/orch hackthon project/backend/db/ghosttrace.db"
                className="mt-1 w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 font-mono text-slate-700 cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* AI & Model Provider */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-slate-900">
            <Cpu className="w-4 h-4 text-purple-600" />
            <span>AI Orchestration & Fallback Engine</span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-600 font-medium">Model Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="mt-1 w-full border border-slate-300 rounded px-3 py-1.5 bg-white focus:outline-none"
              >
                <option value="mock">Deterministic Local Fallback (Recommended for zero-cost offline audit)</option>
                <option value="gemini">Google Gemini (Requires GEMINI_API_KEY)</option>
                <option value="openai">OpenAI (Requires OPENAI_API_KEY)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-600 font-medium">Model Identifier</label>
              <input
                type="text"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="mt-1 w-full border border-slate-300 rounded px-3 py-1.5 font-mono text-slate-700 focus:outline-none"
              />
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-200 text-slate-600">
              <span className="font-semibold text-slate-800">Security Note: </span>
              API credentials are never exposed in browser bundles or client responses. They must be configured securely via backend <code>.env</code> file.
            </div>
          </div>
        </div>

        {/* Privacy & Log Redaction */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-slate-900">
            <Shield className="w-4 h-4 text-emerald-600" />
            <span>Privacy Controls & Execution Batching</span>
          </div>

          <div className="space-y-3 text-xs">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={maskPiiInLogs}
                onChange={(e) => setMaskPiiInLogs(e.target.checked)}
                className="rounded text-[#B76E79] focus:ring-[#B76E79]"
              />
              <span className="text-slate-700 font-medium">Mask customer email and phone numbers in application logs</span>
            </label>

            <div>
              <label className="block text-slate-600 font-medium">Audit Batch Concurrency</label>
              <input
                type="number"
                min={10}
                max={200}
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="mt-1 w-32 border border-slate-300 rounded px-3 py-1.5 font-mono text-slate-700 focus:outline-none focus:border-[#B76E79]"
              />
            </div>
          </div>
        </div>

        {/* Save button */}
        <div className="flex items-center space-x-3">
          <button
            type="submit"
            className="px-5 py-2 text-xs font-semibold text-white bg-gradient-to-r from-[#B76E79] to-[#8C4F5A] rounded hover:opacity-90 transition shadow-sm"
          >
            Save Settings
          </button>
          {saved && (
            <span className="text-xs text-emerald-600 font-semibold flex items-center space-x-1">
              <CheckCircle2 className="w-4 h-4" />
              <span>Settings saved successfully</span>
            </span>
          )}
        </div>
      </form>
    </div>
  );
};
