import React, { useState, useEffect } from 'react';
import { RecommendationItem, ExplanationResponse, CounterfactualResponse } from '../types';
import { apiClient } from '../api/client';
import { X, CheckCircle2, Cpu, TrendingUp, Sparkles, SlidersHorizontal, RefreshCw, AlertCircle, ShieldCheck } from 'lucide-react';

interface WhyRecommendedModalProps {
  item: RecommendationItem | null;
  userId: number;
  onClose: () => void;
}

export const WhyRecommendedModal: React.FC<WhyRecommendedModalProps> = ({ item, userId, onClose }) => {
  const [explanationData, setExplanationData] = useState<ExplanationResponse | null>(null);
  const [loadingExpl, setLoadingExpl] = useState<boolean>(false);
  
  // Counterfactual simulation state
  const [hypoMargin, setHypoMargin] = useState<number>(item?.margin_pct ?? 25);
  const [hypoInventory, setHypoInventory] = useState<number>(item?.inventory_count ?? 50);
  const [counterfactual, setCounterfactual] = useState<CounterfactualResponse | null>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  useEffect(() => {
    if (!item) return;

    setHypoMargin(item.margin_pct ?? 25);
    setHypoInventory(item.inventory_count ?? 50);
    setCounterfactual(null);

    const fetchExplanation = async () => {
      setLoadingExpl(true);
      try {
        const res = await apiClient.get(`/explain/${item.item_id}`, {
          params: { user_id: userId },
        });
        setExplanationData(res.data);
      } catch (err) {
        console.error('Failed to fetch detailed explanation:', err);
      } finally {
        setLoadingExpl(false);
      }
    };

    fetchExplanation();
  }, [item, userId]);

  const handleSimulateCounterfactual = async () => {
    if (!item) return;
    setSimulating(true);
    try {
      const res = await apiClient.get(`/explain/${item.item_id}/counterfactual`, {
        params: {
          user_id: userId,
          hypothetical_margin: hypoMargin,
          hypothetical_inventory: hypoInventory,
        },
      });
      setCounterfactual(res.data);
    } catch (err) {
      console.error('Failed to simulate counterfactual:', err);
    } finally {
      setSimulating(false);
    }
  };

  if (!item) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 my-8">
        {/* Modal Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 uppercase tracking-wider">
                Audited Recommendation Rationale
              </span>
              {item.is_cold_start && (
                <span className="text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-amber-600" />
                  Cold-Start Fallback Active
                </span>
              )}
            </div>
            <h3 className="text-base font-bold text-slate-900 mt-1">
              Why was this item recommended to User #{userId}?
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="py-4 space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          {/* Item Overview */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80 flex items-center justify-between">
            <div>
              <h4 className="text-sm font-bold text-slate-900">{item.name || `Item #${item.item_id}`}</h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Category: <strong className="text-slate-700">{item.category_name}</strong> {item.brand ? `• Brand: ${item.brand}` : ''} • ID: #{item.item_id}
              </p>
            </div>
            <div className="text-right">
              <span className="text-sm font-bold text-slate-900 block">
                ₹{item.price?.toFixed(2) ?? '299.00'}
              </span>
              <span className="text-[11px] text-slate-500 font-medium">
                Stock: {item.inventory_count ?? 50} | Margin: {item.margin_pct ?? 25}%
              </span>
            </div>
          </div>

          {/* Primary Signal Explanation */}
          <div>
            <h5 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Signal-Grounded Explanation
            </h5>
            <div className="p-3 bg-emerald-50/70 text-emerald-950 text-xs rounded-xl border border-emerald-200 flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div className="leading-relaxed">
                {explanationData?.explanation || item.explanation || 'Recommended based on collaborative user affinity and content matching.'}
              </div>
            </div>
          </div>

          {/* Detailed Score Breakdown */}
          <div>
            <h5 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Score Decomposition & ML Signals
            </h5>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-2.5 rounded-xl border border-slate-200/80 bg-white shadow-xs">
                <span className="text-slate-400 block text-[10px] font-medium">Relevance Score</span>
                <span className="text-base font-bold text-blue-600">
                  {(item.relevance_score * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  CF: {item.collaborative_score ? (item.collaborative_score * 100).toFixed(0) + '%' : 'N/A'} • Content: {item.content_score ? (item.content_score * 100).toFixed(0) + '%' : 'N/A'}
                </span>
              </div>

              <div className="p-2.5 rounded-xl border border-slate-200/80 bg-white shadow-xs">
                <span className="text-slate-400 block text-[10px] font-medium">Business Value</span>
                <span className="text-base font-bold text-emerald-600">
                  {((item.business_score ?? 0.5) * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Margin + Inventory + Quality</span>
              </div>

              <div className="p-2.5 rounded-xl border border-slate-200/80 bg-white shadow-xs">
                <span className="text-slate-400 block text-[10px] font-medium">Soft Penalties</span>
                <span className={`text-base font-bold ${item.penalty_score ? 'text-amber-600' : 'text-slate-600'}`}>
                  {item.penalty_score ? `-${(item.penalty_score * 100).toFixed(1)}%` : '0.0%'}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Deficit adjustment</span>
              </div>

              <div className="p-2.5 rounded-xl border border-slate-200/80 bg-slate-900 text-white shadow-xs">
                <span className="text-slate-300 block text-[10px] font-medium">Final Ranking Score</span>
                <span className="text-base font-bold text-white">
                  {(item.final_score * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Rank #{item.rank} in slate</span>
              </div>
            </div>
          </div>

          {/* Interactive Counterfactual Sensitivity Analysis */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center gap-1.5 mb-3">
              <SlidersHorizontal className="w-4 h-4 text-indigo-600" />
              <h5 className="text-xs font-bold text-slate-900">
                Counterfactual Sensitivity Simulation
              </h5>
            </div>
            <p className="text-[11px] text-slate-500 mb-3 leading-normal">
              Test what happens to this item's ranking if inventory or profit margin values change in real time.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-3">
              <div>
                <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                  <span>Simulated Margin:</span>
                  <span className="font-bold text-emerald-700">{hypoMargin.toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="60"
                  step="1"
                  value={hypoMargin}
                  onChange={(e) => setHypoMargin(Number(e.target.value))}
                  className="w-full accent-emerald-600"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                  <span>Simulated Inventory:</span>
                  <span className="font-bold text-slate-900">{hypoInventory} units</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="200"
                  step="5"
                  value={hypoInventory}
                  onChange={(e) => setHypoInventory(Number(e.target.value))}
                  className="w-full accent-slate-800"
                />
              </div>
            </div>

            <button
              onClick={handleSimulateCounterfactual}
              disabled={simulating}
              className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${simulating ? 'animate-spin' : ''}`} />
              {simulating ? 'Simulating Policy Impact...' : 'Simulate Guardrail Sensitivity'}
            </button>

            {counterfactual && (
              <div className="mt-3 p-3 bg-white rounded-lg border border-indigo-100 shadow-xs text-xs space-y-1.5">
                <div className="flex items-center justify-between font-semibold">
                  <span className="text-slate-600">Score Impact:</span>
                  <span className={counterfactual.score_delta >= 0 ? 'text-emerald-600 font-bold' : 'text-rose-600 font-bold'}>
                    {counterfactual.score_delta >= 0 ? `+${(counterfactual.score_delta * 100).toFixed(1)}%` : `${(counterfactual.score_delta * 100).toFixed(1)}%`}
                  </span>
                </div>
                <p className="text-slate-700 text-[11px] leading-relaxed">
                  {counterfactual.summary}
                </p>
                {counterfactual.reasons && counterfactual.reasons.length > 0 && (
                  <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-100">
                    Triggers: {counterfactual.reasons.join(' • ')}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
