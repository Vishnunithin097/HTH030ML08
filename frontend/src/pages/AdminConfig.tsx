import React, { useState } from 'react';
import { GuardrailConfigPanel } from '../components/GuardrailConfigPanel';
import { BusinessImpactSimulatorPanel } from '../components/BusinessImpactSimulatorPanel';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import { Sliders, Calculator } from 'lucide-react';

export const AdminConfig: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState<'guardrails' | 'simulator'>('guardrails');

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Sub-Navigation Tabs */}
      <div className="flex border-b border-slate-200 bg-white rounded-t-xl px-4 pt-2 shadow-2xs">
        <button
          onClick={() => setActiveTab('guardrails')}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-colors cursor-pointer ${
            activeTab === 'guardrails'
              ? 'border-slate-900 text-slate-900'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <Sliders className="w-4 h-4" />
          Guardrail Policy & Controls
        </button>

        <button
          onClick={() => setActiveTab('simulator')}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-colors cursor-pointer ${
            activeTab === 'simulator'
              ? 'border-emerald-700 text-emerald-800'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <Calculator className="w-4 h-4" />
          Business Impact Simulator
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'guardrails' ? (
        <GuardrailConfigPanel />
      ) : (
        <BusinessImpactSimulatorPanel />
      )}
    </div>
  );
};
