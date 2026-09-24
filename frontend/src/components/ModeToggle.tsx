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
    <div className="inline-flex items-center bg-slate-100/90 p-0.5 rounded-lg border border-slate-200">
      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange('pure')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
          mode === 'pure'
            ? 'bg-white text-slate-900 shadow-2xs font-semibold'
            : 'text-slate-600 hover:text-slate-900'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <Sparkles className="w-3.5 h-3.5 text-slate-500" />
        <span>Pure Relevance</span>
      </button>

      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange('business_aware')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
          mode === 'business_aware'
            ? 'bg-emerald-700 text-white shadow-2xs font-semibold'
            : 'text-slate-600 hover:text-slate-900'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-200" />
        <span>Business-Aware</span>
      </button>
    </div>
  );
};
