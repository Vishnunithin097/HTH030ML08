import React, { useState, useEffect } from 'react';
import { GuardrailConfig } from '../types';
import { apiClient } from '../api/client';
import { Sliders, ShieldCheck, Save, Check } from 'lucide-react';

export const GuardrailConfigPanel: React.FC = () => {
  const [config, setConfig] = useState<GuardrailConfig | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await apiClient.get('/config/guardrails');
      setConfig(res.data);
    } catch (e) {
      console.error('Failed to load guardrails config:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    setSavedSuccess(false);
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
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e) {
      console.error('Failed to update guardrails config:', e);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) {
    return <div className="p-6 bg-white rounded-xl border border-slate-200 animate-pulse">Loading guardrail settings...</div>;
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-emerald-600" />
          <h3 className="text-base font-bold text-slate-900">Business Guardrails Control Center</h3>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-semibold hover:bg-emerald-700 transition-colors disabled:opacity-50"
        >
          {savedSuccess ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : savedSuccess ? 'Saved' : 'Apply Guardrails'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Minimum Inventory Threshold (Units)
          </label>
          <input
            type="number"
            value={config.min_inventory}
            onChange={(e) => setConfig({ ...config, min_inventory: Number(e.target.value) })}
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          />
          <p className="text-[11px] text-slate-400 mt-1">Items below this inventory count receive penalties or are filtered.</p>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Minimum Profit Margin (%)
          </label>
          <input
            type="number"
            step="0.1"
            value={config.min_margin}
            onChange={(e) => setConfig({ ...config, min_margin: Number(e.target.value) })}
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          />
          <p className="text-[11px] text-slate-400 mt-1">Items below this margin floor are prioritized lower.</p>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            ML Relevance Weight ({config.relevance_weight})
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={config.relevance_weight}
            onChange={(e) => {
              const rel = Number(e.target.value);
              setConfig({ ...config, relevance_weight: rel, business_weight: Number((1 - rel).toFixed(2)) });
            }}
            className="w-full"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Business Weight ({config.business_weight})
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={config.business_weight}
            onChange={(e) => {
              const biz = Number(e.target.value);
              setConfig({ ...config, business_weight: biz, relevance_weight: Number((1 - biz).toFixed(2)) });
            }}
            className="w-full"
          />
        </div>

        <div className="md:col-span-2 pt-2 border-t border-slate-100 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-800 block">Strict Hard Filtering</span>
            <span className="text-[11px] text-slate-400">Strictly drop items that do not meet min inventory or margin criteria.</span>
          </div>
          <input
            type="checkbox"
            checked={config.hard_filter_enabled}
            onChange={(e) => setConfig({ ...config, hard_filter_enabled: e.target.checked })}
            className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
          />
        </div>
      </div>
    </div>
  );
};
