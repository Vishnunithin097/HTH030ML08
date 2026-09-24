import React, { useState, useEffect } from 'react';
import { GuardrailConfig } from '../types';
import { apiClient } from '../api/client';
import { Sliders, ShieldCheck, Save, Check, AlertCircle, Info, RefreshCw, CheckCircle2 } from 'lucide-react';

export const GuardrailConfigPanel: React.FC = () => {
  const [config, setConfig] = useState<GuardrailConfig | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get('/config/guardrails');
      setConfig(res.data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to load guardrail configuration.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    setSavedSuccess(false);
    setError(null);
    try {
      const res = await apiClient.put('/config/guardrails', {
        min_inventory: Number(config.min_inventory),
        min_margin: Number(config.min_margin),
        relevance_weight: Number(config.relevance_weight),
        business_weight: Number(config.business_weight),
        margin_weight: Number(config.margin_weight),
        inventory_weight: Number(config.inventory_weight),
        quality_weight: Number(config.quality_weight),
        hard_filter_enabled: Boolean(config.hard_filter_enabled),
      });
      setConfig(res.data);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 4000);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to update guardrails. Ensure you are signed in as an Admin.');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-xs text-center animate-pulse">
        <RefreshCw className="w-6 h-6 text-slate-400 mx-auto mb-2 animate-spin" />
        <span className="text-xs text-slate-500 font-medium">Fetching guardrail configuration parameters...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Panel Header */}
      <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50/50">
        <div>
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-slate-800" />
            <h3 className="text-base font-bold text-slate-900">
              Business Guardrail Configuration & Policy Control
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Configure multi-objective ranking weights, inventory protection floors, and margin thresholds.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {savedSuccess && (
            <span className="text-xs text-emerald-700 font-semibold flex items-center gap-1 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Policy Updated
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
          >
            {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {saving ? 'Applying...' : 'Save & Publish Guardrails'}
          </button>
        </div>
      </div>

      {error && (
        <div className="m-6 p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <div>{error}</div>
        </div>
      )}

      {/* Settings Grid */}
      <div className="p-6 space-y-6">
        {/* Section 1: Thresholds */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
            Threshold Rules & Protection Floors
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/30">
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-bold text-slate-900">
                  Minimum Inventory Floor (Units)
                </label>
                <span className="text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                  {config.min_inventory} units
                </span>
              </div>
              <input
                type="number"
                min="0"
                max="500"
                value={config.min_inventory}
                onChange={(e) => setConfig({ ...config, min_inventory: Number(e.target.value) })}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none mb-1.5"
              />
              <p className="text-[11px] text-slate-500 leading-normal">
                Allowed range: 0 - 500 units. Items below this threshold will trigger stockout deficit penalties or hard exclusion.
              </p>
            </div>

            <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/30">
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-bold text-slate-900">
                  Minimum Profit Margin Floor (%)
                </label>
                <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  {config.min_margin}%
                </span>
              </div>
              <input
                type="number"
                step="0.5"
                min="0"
                max="50"
                value={config.min_margin}
                onChange={(e) => setConfig({ ...config, min_margin: Number(e.target.value) })}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none mb-1.5"
              />
              <p className="text-[11px] text-slate-500 leading-normal">
                Allowed range: 0.0% - 50.0%. Items below this margin floor receive margin deficit penalties.
              </p>
            </div>
          </div>
        </div>

        {/* Section 2: Macro Multi-Objective Weights */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
            Macro Multi-Objective Re-Ranking Balance
          </h4>
          <div className="p-5 rounded-xl border border-slate-200/80 bg-slate-50/40 space-y-4">
            <div>
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate-700">ML Relevance Weight vs Business Objective Weight</span>
                <span className="text-slate-900 font-bold font-mono">
                  Relevance: {(config.relevance_weight * 100).toFixed(0)}% | Business: {(config.business_weight * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={config.relevance_weight}
                onChange={(e) => {
                  const rel = Number(e.target.value);
                  setConfig({
                    ...config,
                    relevance_weight: rel,
                    business_weight: Number((1 - rel).toFixed(2)),
                  });
                }}
                className="w-full accent-slate-900"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>0% Relevance (Pure Business)</span>
                <span>50% Blended</span>
                <span>100% Relevance (Pure ML)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Business Sub-Weights */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
            Business Factor Sub-Weights
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-xl border border-slate-200/80 bg-white shadow-2xs">
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Margin Weight</span>
                <span className="font-bold text-emerald-700">{(config.margin_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={config.margin_weight}
                onChange={(e) => setConfig({ ...config, margin_weight: Number(e.target.value) })}
                className="w-full accent-emerald-600 mb-1"
              />
              <span className="text-[10px] text-slate-400">Yield prioritization</span>
            </div>

            <div className="p-3.5 rounded-xl border border-slate-200/80 bg-white shadow-2xs">
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Inventory Weight</span>
                <span className="font-bold text-blue-700">{(config.inventory_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={config.inventory_weight}
                onChange={(e) => setConfig({ ...config, inventory_weight: Number(e.target.value) })}
                className="w-full accent-blue-600 mb-1"
              />
              <span className="text-[10px] text-slate-400">Stockout mitigation</span>
            </div>

            <div className="p-3.5 rounded-xl border border-slate-200/80 bg-white shadow-2xs">
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Quality Weight</span>
                <span className="font-bold text-amber-700">{(config.quality_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={config.quality_weight}
                onChange={(e) => setConfig({ ...config, quality_weight: Number(e.target.value) })}
                className="w-full accent-amber-600 mb-1"
              />
              <span className="text-[10px] text-slate-400">Catalog quality factor</span>
            </div>
          </div>
        </div>

        {/* Section 4: Hard Filter Switch */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-between p-4 bg-slate-50/60 rounded-xl border border-slate-200/80">
          <div>
            <span className="text-xs font-bold text-slate-900 block">Strict Hard Constraint Filtering</span>
            <span className="text-[11px] text-slate-500">
              When enabled, items violating minimum inventory or margin thresholds are completely pruned from the recommendation slate rather than receiving soft penalties.
            </span>
          </div>
          <label className="relative inline-flex items-center cursor-pointer shrink-0 ml-4">
            <input
              type="checkbox"
              checked={config.hard_filter_enabled}
              onChange={(e) => setConfig({ ...config, hard_filter_enabled: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
          </label>
        </div>
      </div>
    </div>
  );
};
