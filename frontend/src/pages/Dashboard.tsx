import React, { useState, useEffect } from 'react';
import { RecommendationMode, RecommendationItem, User, CatalogItemResponse, RecommendationResponse } from '../types';
import { ModeToggle } from '../components/ModeToggle';
import { RecommendationList } from '../components/RecommendationList';
import { WhyRecommendedModal } from '../components/WhyRecommendedModal';
import { ScoreBreakdownChart } from '../components/ScoreBreakdownChart';
import { apiClient } from '../api/client';
import { UserCheck, Sparkles, Search, ShieldCheck, AlertTriangle, CheckCircle, TrendingUp, Package, RefreshCw, X } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [selectedUserId, setSelectedUserId] = useState<number>(999999999);
  const [users, setUsers] = useState<User[]>([]);
  const [mode, setMode] = useState<RecommendationMode>('business_aware');
  const [activeModalItem, setActiveModalItem] = useState<RecommendationItem | null>(null);
  
  // Recommendations state
  const [recoResponse, setRecoResponse] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<CatalogItemResponse[]>([]);
  const [searching, setSearching] = useState<boolean>(false);
  const [showSearchModal, setShowSearchModal] = useState<boolean>(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    fetchRecommendations();
  }, [selectedUserId, mode]);

  const fetchUsers = async () => {
    try {
      const res = await apiClient.get('/users?limit=15');
      setUsers(res.data);
    } catch (e) {
      console.error('Failed to fetch user list:', e);
    }
  };

  const fetchRecommendations = async () => {
    if (!selectedUserId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get('/recommendations', {
        params: { user_id: selectedUserId, mode, limit: 12 },
      });
      setRecoResponse(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load recommendations.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    setShowSearchModal(true);
    try {
      const res = await apiClient.get('/items', {
        params: { search: searchQuery.trim(), limit: 12 },
      });
      setSearchResults(res.data);
    } catch (e) {
      console.error('Failed to search items:', e);
    } finally {
      setSearching(false);
    }
  };

  const currentUser = users.find((u) => u.user_id === selectedUserId);
  const isColdUser = selectedUserId === 999999999 || currentUser?.is_synthetic_cold_demo || recoResponse?.cold_start;

  return (
    <div className="space-y-6">
      {/* Top Header Controls Bar */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: User Selector & Search */}
        <div className="flex flex-wrap items-center gap-3">
          {/* User selector */}
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 text-xs">
            <UserCheck className="w-4 h-4 text-slate-500" />
            <span className="font-semibold text-slate-700">Active Shopper:</span>
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(Number(e.target.value))}
              className="bg-transparent font-medium text-slate-900 focus:outline-none cursor-pointer pr-1"
            >
              <option value={999999999}>Demo Cold Shopper (#999999999)</option>
              {users
                .filter((u) => u.user_id !== 999999999)
                .map((u) => (
                  <option key={u.user_id} value={u.user_id}>
                    User #{u.user_id} {u.is_synthetic_cold_demo ? '(Cold Demo)' : `(${u.selected_categories?.length ? u.selected_categories[0] : 'Warm User'})`}
                  </option>
                ))}
            </select>
          </div>

          {/* Catalog Search Form */}
          <form onSubmit={handleSearch} className="flex items-center gap-1.5">
            <div className="relative">
              <input
                type="text"
                placeholder="Search catalog items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-48 sm:w-60 px-3 py-1.5 pl-8 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
              />
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            </div>
            <button
              type="submit"
              disabled={searching}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
            >
              Search
            </button>
          </form>
        </div>

        {/* Right: Mode Switcher */}
        <div className="flex items-center gap-3">
          <ModeToggle mode={mode} onChange={setMode} disabled={loading} />
        </div>
      </div>

      {/* Shopper Status Context Card */}
      <div className="bg-slate-900 text-white rounded-xl p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono font-bold text-emerald-400">
              PROFILE: USER #{selectedUserId}
            </span>
            {isColdUser ? (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">
                <Sparkles className="w-3 h-3" /> Cold Start (Zero Interaction History)
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
                <CheckCircle className="w-3 h-3" /> Warm Profile ({recoResponse?.interaction_count ?? 12} interactions)
              </span>
            )}
          </div>
          <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
            {isColdUser
              ? 'Cold-start mode active. Recommendations resolve via user category affinity profiling and catalog metadata fallback.'
              : 'Collaborative SVD factor dot-products blended with content TF-IDF semantic embeddings.'}
          </p>
        </div>

        <div className="text-left sm:text-right shrink-0">
          <span className="text-[10px] text-slate-400 block font-medium uppercase tracking-wider">
            Re-Ranking Mode
          </span>
          <span className="text-sm font-bold text-white flex items-center gap-1.5 sm:justify-end mt-0.5">
            {mode === 'business_aware' ? (
              <>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Business-Aware Guardrails
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-blue-400" />
                Pure Relevance (ML Only)
              </>
            )}
          </span>
        </div>
      </div>

      {/* Guardrail Health Status Banner if available */}
      {recoResponse?.guardrail_health && (
        <div
          className={`p-3.5 rounded-xl border text-xs flex items-center justify-between gap-3 ${
            recoResponse.guardrail_health.health_status === 'healthy'
              ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
              : 'bg-amber-50/80 border-amber-200 text-amber-900'
          }`}
        >
          <div className="flex items-center gap-2">
            {recoResponse.guardrail_health.health_status === 'healthy' ? (
              <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            )}
            <span className="font-medium">
              <strong>Guardrail Health:</strong> {recoResponse.guardrail_health.health_message}
            </span>
          </div>

          <div className="text-[11px] font-mono shrink-0 hidden md:block">
            Churn: {recoResponse.guardrail_health.churn_count} items • Suppression Rate: {(recoResponse.guardrail_health.suppression_rate * 100).toFixed(1)}%
          </div>
        </div>
      )}

      {/* Financial Simulation / Projection Bar */}
      {recoResponse?.gmv_projection && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[10px] text-slate-400 font-semibold block uppercase">Projected GMV</span>
            <span className="text-base font-bold text-slate-900 font-mono">
              ₹{recoResponse.gmv_projection.projected_gmv.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Top-12 slate projection</span>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[10px] text-slate-400 font-semibold block uppercase">Projected Margin Yield</span>
            <span className="text-base font-bold text-emerald-600 font-mono">
              ₹{recoResponse.gmv_projection.projected_margin_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Estimated gross margin</span>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[10px] text-slate-400 font-semibold block uppercase">Avg Slate Margin</span>
            <span className="text-base font-bold text-slate-900 font-mono">
              {recoResponse.gmv_projection.avg_margin_pct.toFixed(1)}%
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Portfolio profitability</span>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[10px] text-slate-400 font-semibold block uppercase">Stockout Risk Items</span>
            <span className={`text-base font-bold font-mono ${recoResponse.gmv_projection.stockout_risk_items > 0 ? 'text-amber-600' : 'text-emerald-600'}`}>
              {recoResponse.gmv_projection.stockout_risk_items} items
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Below inventory floor</span>
          </div>
        </div>
      )}

      {/* Main Recommendation Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recommended Products</h3>
            <p className="text-xs text-slate-500">
              Personalized candidate ranking evaluated using {mode === 'business_aware' ? 'Multi-Objective Guardrail Re-Ranker' : 'Pure ML Relevance'}.
            </p>
          </div>
          <button
            onClick={fetchRecommendations}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold border border-slate-200 shadow-2xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Feed
          </button>
        </div>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
            {error}
          </div>
        )}

        <RecommendationList
          items={recoResponse?.recommendations || []}
          loading={loading}
          onExplainClick={(item) => setActiveModalItem(item)}
        />
      </div>

      {/* Score Breakdown Visualization */}
      {recoResponse?.recommendations && recoResponse.recommendations.length > 0 && (
        <ScoreBreakdownChart items={recoResponse.recommendations} />
      )}

      {/* Explainability Audit Modal */}
      <WhyRecommendedModal
        item={activeModalItem}
        userId={selectedUserId}
        onClose={() => setActiveModalItem(null)}
      />

      {/* Catalog Search Results Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 my-8">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Catalog Search Results for "{searchQuery}"
                </h3>
                <p className="text-xs text-slate-500">Found {searchResults.length} matching products in catalog database.</p>
              </div>
              <button
                onClick={() => setShowSearchModal(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 max-h-[60vh] overflow-y-auto space-y-2">
              {searching ? (
                <div className="py-12 text-center text-xs text-slate-400">Searching catalog...</div>
              ) : searchResults.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-500">No catalog products found matching query.</div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {searchResults.map((p) => (
                    <div key={p.item_id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                      <div className="font-bold text-slate-900 line-clamp-1">{p.name}</div>
                      <div className="text-slate-500 text-[11px] mb-1.5">{p.category_name} • #{p.item_id}</div>
                      <div className="flex justify-between items-center text-slate-700 font-medium">
                        <span>₹{p.price.toFixed(2)}</span>
                        <span>Margin: {p.margin_pct ?? 25}% | Stock: {p.inventory_count ?? 100}u</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setShowSearchModal(false)}
                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold"
              >
                Close Search
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
