import React, { useState } from 'react';
import { Navigation } from './components/Navigation';
import { Overview } from './pages/Overview';
import { CaseExplorer } from './pages/CaseExplorer';
import { CaseInvestigation } from './pages/CaseInvestigation';
import { SystemsFlows } from './pages/SystemsFlows';
import { AnalysisRuns } from './pages/AnalysisRuns';
import { EvaluationLab } from './pages/EvaluationLab';
import { SubmissionCenter } from './pages/SubmissionCenter';
import { Settings } from './pages/Settings';
import { CsvUploadModal } from './components/CsvUploadModal';
import { ShieldCheck, Database, UploadCloud } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>('case_001');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const handleSelectCase = (caseId: string) => {
    setSelectedCaseId(caseId);
    setCurrentTab('investigation');
  };

  return (
    <div className="flex h-screen bg-[#F8F9FA] overflow-hidden">
      {/* Sidebar Navigation */}
      <Navigation
        currentTab={currentTab}
        onSelectTab={(tab) => setCurrentTab(tab)}
        selectedCaseId={selectedCaseId}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header Bar */}
        <header className="h-14 bg-white/95 backdrop-blur-xs border-b border-[#EFE4E6] px-8 flex items-center justify-between shrink-0 shadow-xs">
          <div className="flex items-center space-x-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[#9E7A81]">
              Audit Scope:
            </span>
            <span className="px-2.5 py-0.5 rounded text-xs font-mono font-medium bg-[#FAF0F2] text-[#89434E] border border-[#EAC5CB]">
              Northstar Shop Enterprise
            </span>
            <span className="text-[#E0CFD2]">|</span>
            <span className="text-xs text-[#8C6D73] font-mono">
              Cutoff: 2026-10-08T11:00:00Z
            </span>
          </div>

          <div className="flex items-center space-x-3">
            {/* Global CSV Upload Action in Rose Gold */}
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="px-3.5 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-[#B76E79] to-[#9E5762] hover:from-[#A85E69] hover:to-[#8E4954] rounded-lg transition-all flex items-center space-x-1.5 shadow-sm"
            >
              <UploadCloud className="w-3.5 h-3.5 text-white" />
              <span>Upload & Audit CSV</span>
            </button>

            <div className="flex items-center space-x-1.5 text-xs text-[#0D6847] bg-[#F2FAF6] px-2.5 py-1 rounded-full border border-[#C2ECD8] font-medium">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span>Engine Status: Verified Clean</span>
            </div>
          </div>
        </header>

        {/* Scrollable View Container */}
        <main className="flex-1 overflow-y-auto">
          {currentTab === 'overview' && (
            <Overview
              onNavigate={(tab, caseId) => {
                if (caseId) setSelectedCaseId(caseId);
                setCurrentTab(tab);
              }}
              onOpenUpload={() => setIsUploadModalOpen(true)}
            />
          )}

          {currentTab === 'cases' && (
            <CaseExplorer
              onSelectCase={handleSelectCase}
              onOpenUpload={() => setIsUploadModalOpen(true)}
            />
          )}

          {currentTab === 'investigation' && selectedCaseId && (
            <CaseInvestigation
              caseId={selectedCaseId}
              onBack={() => setCurrentTab('cases')}
            />
          )}

          {currentTab === 'systems' && <SystemsFlows />}

          {currentTab === 'runs' && <AnalysisRuns />}

          {currentTab === 'evaluation' && <EvaluationLab />}

          {currentTab === 'submission' && <SubmissionCenter />}

          {currentTab === 'settings' && <Settings />}
        </main>

        {/* Global Footer in Rose Gold & White */}
        <footer className="h-9 bg-white border-t border-[#EFE4E6] px-8 flex items-center justify-between shrink-0 text-xs text-[#8C6D73] shadow-xs">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-[#6E3640]">GhostTrace AI</span>
            <span className="text-[#E0CFD2]">•</span>
            <span>Enterprise Privacy Compliance Platform</span>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-[#4A2027]">
            <span>Platform Architect</span>
            <span className="text-[#C0B3B6]">|</span>
            <span className="font-medium">Made by <span className="font-bold text-[#B76E79]">Shrey Gadhiya</span></span>
          </div>
        </footer>
      </div>

      {/* CSV File Upload Modal */}
      <CsvUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSelectCase={handleSelectCase}
      />
    </div>
  );
};

export default App;
