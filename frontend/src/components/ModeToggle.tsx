import React from 'react';
import { RecommendationMode } from '../types';
import { Sparkles, ShieldCheck } from 'lucide-react';

interface ModeToggleProps {
  mode: RecommendationMode;
  onChange: (mode: RecommendationMode) => void;
}

export const ModeToggle: React.FC<ModeToggleProps> = ({ mode, onChange }) => {
  return (
    <div className="inline-flex bg-slate-100 p-1 rounded-xl border border-slate-200">
      <button
        onClick={() => onChange('pure')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
          mode === 'pure'
            ? 'bg-white text-slate-900 shadow-sm'
            : 'text-slate-600 hover:text-slate-900'
        }`}
      >
        <Sparkles className="w-3.5 h-3.5 text-blue-500" />
        Pure Relevance (ML Only)
      </button>
      <button
        onClick={() => onChange('business_aware')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
          mode === 'business_aware'
            ? 'bg-emerald-600 text-white shadow-sm'
            : 'text-slate-600 hover:text-slate-900'
        }`}
      >
        <ShieldCheck className="w-3.5 h-3.5" />
        Business-Aware (Guardrails Active)
      </button>
    </div>
  );
};
