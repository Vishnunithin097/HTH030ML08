import React from 'react';
import { RecommendationMode } from '../types';
import { Sparkles, ShieldCheck } from 'lucide-react';

interface ModeToggleProps {
  mode: RecommendationMode;
  onChange: (mode: RecommendationMode) => void;
  disabled?: boolean;
}

export const ModeToggle: React.FC<ModeToggleProps> = ({ mode, onChange, disabled }) => {
  return (
    <div className="inline-flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-sm">
      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange('pure')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
          mode === 'pure'
            ? 'bg-white text-slate-900 shadow-xs'
            : 'text-slate-600 hover:text-slate-900'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <Sparkles className="w-3.5 h-3.5 text-blue-600" />
        <span>Pure ML Relevance</span>
      </button>

      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange('business_aware')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
          mode === 'business_aware'
            ? 'bg-emerald-700 text-white shadow-xs'
            : 'text-slate-600 hover:text-slate-900'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-200" />
        <span>Business-Aware (Guardrails Active)</span>
      </button>
    </div>
  );
};
