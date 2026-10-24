import React from 'react';
import {
  LayoutDashboard,
  FolderSearch,
  Network,
  History,
  TestTube2,
  FileArchive,
  Settings as SettingsIcon,
  CheckCircle2,
  AlertTriangle,
  FileText
} from 'lucide-react';
import { Logo } from './Logo';

interface NavigationProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  selectedCaseId?: string | null;
}

export const Navigation: React.FC<NavigationProps> = ({ currentTab, onSelectTab, selectedCaseId }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'cases', label: 'Case Explorer', icon: FolderSearch },
    { id: 'systems', label: 'Systems & Data Flows', icon: Network },
    { id: 'runs', label: 'Analysis Runs', icon: History },
    { id: 'evaluation', label: 'Evaluation Lab', icon: TestTube2 },
    { id: 'submission', label: 'Submission Center', icon: FileArchive },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-[#191013] text-[#D4B6BC] flex flex-col border-r border-[#311A20] shrink-0 select-none">
      {/* Brand Header with Bespoke Rose Gold Emblem */}
      <div className="p-4 border-b border-[#311A20] flex items-center justify-between">
        <Logo size={36} showText={true} subtitle="Forensic Audit Platform" />
      </div>

      {/* Navigation Links */}
      <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-[#9E7A81]">
          Forensic Operations
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all text-left ${
                isActive
                  ? 'bg-gradient-to-r from-[#321B22] to-[#26141A] text-white font-semibold shadow-xs border-l-2 border-[#B76E79]'
                  : 'text-[#B89CA3] hover:text-[#FFF0F2] hover:bg-[#25151B]'
              }`}
            >
              <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-[#E2A6AF]' : 'text-[#8C6B72]'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}

        {selectedCaseId && (
          <div className="pt-4">
            <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#9E7A81]">
              Active Investigation
            </div>
            <button
              onClick={() => onSelectTab('investigation')}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all text-left ${
                currentTab === 'investigation'
                  ? 'bg-[#3A1E26] text-[#F4D0D5] border border-[#683641]'
                  : 'text-[#B89CA3] hover:text-[#FFF0F2] hover:bg-[#25151B]'
              }`}
            >
              <FileText className="w-4 h-4 text-[#D89FA7]" />
              <span className="truncate font-mono text-xs">{selectedCaseId}</span>
            </button>
          </div>
        )}
      </nav>

      {/* Compliance Protocol Badge & Developer Credit */}
      <div className="p-4 border-t border-[#311A20] bg-[#140C0E]/70">
        <div className="flex items-center justify-between text-xs text-[#B89CA3]">
          <span className="font-medium">GDPR & CCPA Scope</span>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#2B151B] text-[#E2A6AF] border border-[#522832]">
            v1.0-ORD
          </span>
        </div>
        <p className="text-[11px] text-[#8C6D73] mt-1.5 leading-relaxed">
          Ground-truth evidence audit engine. 518 cases verified.
        </p>
        <div className="mt-3 pt-2.5 border-t border-[#2B151B] flex items-center justify-between text-[11px]">
          <span className="text-[#8C6D73]">Platform</span>
          <span className="text-[#E2A6AF] font-medium tracking-wide">
            Made by <span className="font-bold text-white underline decoration-[#B76E79]">Shrey Gadhiya</span>
          </span>
        </div>
      </div>
    </aside>
  );
};
