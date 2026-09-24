import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { RecommendationMode, RecommendationItem, User, CatalogItemResponse, RecommendationResponse } from '../types';
import { ModeToggle } from '../components/ModeToggle';
import { RecommendationList } from '../components/RecommendationList';
import { WhyRecommendedModal } from '../components/WhyRecommendedModal';
import { ScoreBreakdownChart } from '../components/ScoreBreakdownChart';
import { ProductImage } from '../components/ProductImage';
import { apiClient } from '../api/client';
import { UserCheck, Sparkles, Search, ShieldCheck, CheckCircle2, TrendingUp, RefreshCw, X, ShoppingBag, Tag } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlUserId = searchParams.get('user_id');
  const storedUserId = localStorage.getItem('active_shopper_id');

  const initialUserId = urlUserId
    ? Number(urlUserId)
    : storedUserId
    ? Number(storedUserId)
    : 111016;

  const [selectedUserId, setSelectedUserId] = useState<number>(initialUserId);
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
    if (urlUserId && Number(urlUserId) !== selectedUserId) {
      setSelectedUserId(Number(urlUserId));
    }
  }, [urlUserId]);

  useEffect(() => {
    localStorage.setItem('active_shopper_id', selectedUserId.toString());
    fetchRecommendations();
  }, [selectedUserId, mode]);

  const fetchUsers = async () => {
    try {
      const res = await apiClient.get('/users?limit=30');
      setUsers(res.data);
      if (res.data.length > 0 && !selectedUserId) {
        setSelectedUserId(res.data[0].user_id);
      }
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
  
  // Authoritative selected interests from API or active user profile
  const activeInterests: string[] = recoResponse?.selected_categories && recoResponse.selected_categories.length > 0
    ? recoResponse.selected_categories
    : (currentUser?.selected_categories || []);

  return (
    <div className="space-y-6 w-full mx-auto">
      {/* Top Header Controls Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Shopper Selector & Search */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Shopper Selector */}
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 text-xs">
            <UserCheck className="w-4 h-4 text-slate-500" />
            <span className="font-medium text-slate-600">Shopper:</span>
            <select
              value={selectedUserId}
              onChange={(e) => {
                const newId = Number(e.target.value);
                setSelectedUserId(newId);
                setSearchParams({ user_id: newId.toString() });
              }}
              className="bg-transparent font-semibold text-slate-900 focus:outline-none cursor-pointer pr-1"
            >
              {users.map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  Shopper #{u.user_id} {u.is_synthetic_cold_demo ? `(Cold Start · ${u.selected_categories?.join(', ') || 'Zero History'})` : `(Warm Profile · ${u.selected_categories?.length ? u.selected_categories.join(', ') : 'Catalog'})`}
                </option>
              ))}
              {!users.some((u) => u.user_id === selectedUserId) && (
                <option value={selectedUserId}>Shopper #{selectedUserId} (Active Persona)</option>
              )}
            </select>
          </div>

          {/* Catalog Search */}
          <form onSubmit={handleSearch} className="flex items-center gap-1.5">
            <div className="relative">
              <input
                type="text"
                placeholder="Search catalog items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-48 sm:w-60 px-3 py-1.5 pl-8 text-xs border border-slate-200 rounded-lg focus:ring-1 focus:ring-emerald-600 focus:border-emerald-600 focus:outline-none bg-white"
              />
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            </div>
            <button
              type="submit"
              disabled={searching}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors"
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

      {/* Shopper Profile Status Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-slate-900">
              Active Session: Shopper #{selectedUserId}
            </span>
            {isColdUser ? (
              <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-amber-50 text-amber-800 px-2 py-0.5 rounded border border-amber-200/70">
                <Sparkles className="w-3 h-3 text-amber-600" /> Cold Start (Zero History)
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded border border-emerald-200/70">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Warm Profile ({recoResponse?.interaction_count ?? 12} interactions)
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            {isColdUser
              ? 'Zero historical transactions. Candidates routed via stated category preferences and TF-IDF content similarity.'
              : 'Collaborative SVD latent representations fused with BigBasket TF-IDF content matching.'}
          </p>
          
          {/* Interests Badges */}
          <div className="flex flex-wrap items-center gap-1.5 mt-2.5 pt-2 border-t border-slate-100">
            <span className="text-[11px] font-medium text-slate-500 mr-1 flex items-center gap-1">
              <Tag className="w-3 h-3 text-slate-400" /> Interests:
            </span>
            {activeInterests.length > 0 ? (
              activeInterests.map((cat, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-800 border border-slate-200 shadow-2xs"
                >
                  {cat}
                </span>
              ))
            ) : (
              <span className="text-[11px] text-slate-400 italic">General Catalog</span>
            )}
          </div>
        </div>

        <div className="text-left sm:text-right shrink-0">
          <span className="text-[11px] text-slate-400 block font-normal">Active Pipeline</span>
          <span className="text-xs font-semibold text-slate-900 flex items-center gap-1 sm:justify-end mt-0.5">
            {mode === 'business_aware' ? (
              <>
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Business Guardrails Active
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-slate-500" />
                Pure Relevance Mode
              </>
            )}
          </span>
        </div>
      </div>

      {/* Commercial Telemetry & Guardrail Summary in Business Mode */}
      {mode === 'business_aware' && recoResponse?.gmv_projection && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
            <span className="text-[11px] text-slate-400 font-medium block">Projected Slate GMV</span>
            <span className="text-base font-semibold text-slate-900">
              ₹{recoResponse.gmv_projection.projected_gmv.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Top-12 slate projection</span>
          </div>

          <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
            <span className="text-[11px] text-slate-400 font-medium block">Projected Margin Yield</span>
            <span className="text-base font-semibold text-emerald-700">
              ₹{recoResponse.gmv_projection.projected_margin_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Commercial margin</span>
          </div>

          <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
            <span className="text-[11px] text-slate-400 font-medium block">Avg Slate Margin</span>
            <span className="text-base font-semibold text-slate-900">
              {recoResponse.gmv_projection.avg_margin_pct.toFixed(1)}%
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Portfolio profitability</span>
          </div>

          <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
            <span className="text-[11px] text-slate-400 font-medium block">Stockout Risk SKUs</span>
            <span className={`text-base font-semibold ${recoResponse.gmv_projection.stockout_risk_items > 0 ? 'text-amber-700' : 'text-emerald-700'}`}>
              {recoResponse.gmv_projection.stockout_risk_items} SKUs
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Inventory constraints applied</span>
          </div>
        </div>
      )}

      {/* Main Recommendations Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Recommended For You</h2>
            <p className="text-xs text-slate-500">
              {mode === 'business_aware'
                ? 'Personalized products re-ranked with inventory, margin, and quality safeguards.'
                : 'Personalized products ranked strictly by pure ML recommendation score.'}
            </p>
          </div>
          <button
            onClick={fetchRecommendations}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 text-slate-700 rounded-md text-xs font-medium border border-slate-200 shadow-2xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {error && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800">
            {error}
          </div>
        )}

        <RecommendationList
          items={recoResponse?.recommendations || []}
          loading={loading}
          mode={mode}
          onExplainClick={(item) => setActiveModalItem(item)}
        />
      </div>

      {/* Progressive Score Breakdown Chart */}
      {recoResponse?.recommendations && recoResponse.recommendations.length > 0 && (
        <div className="pt-2">
          <ScoreBreakdownChart items={recoResponse.recommendations} />
        </div>
      )}

      {/* Why Recommended Modal */}
      <WhyRecommendedModal
        item={activeModalItem}
        userId={selectedUserId}
        onClose={() => setActiveModalItem(null)}
      />

      {/* Catalog Search Results Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 overflow-y-auto">
          <div className="bg-white rounded-xl max-w-3xl w-full p-6 shadow-xl border border-slate-200 my-8">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="text-base font-semibold text-slate-900">
                  Catalog Search Results for "{searchQuery}"
                </h3>
                <p className="text-xs text-slate-500">Found {searchResults.length} matching products in catalog database.</p>
              </div>
              <button
                onClick={() => setShowSearchModal(false)}
                className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100"
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
                    <div key={p.item_id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex gap-3 items-center">
                      <div className="w-14 h-14 rounded bg-white border border-slate-200 shrink-0 overflow-hidden">
                        <ProductImage
                          productId={p.item_id}
                          productName={p.name}
                          category={p.category_name}
                          imageUrl={p.image_url}
                          imageStatus={p.image_status}
                          className="w-full h-full"
                        />
                      </div>
                      <div className="flex-1 min-w-0 text-xs">
                        <div className="font-semibold text-slate-900 line-clamp-1">{p.name}</div>
                        <div className="text-slate-500 text-[11px] mb-1">{p.category_name} • SKU #{p.item_id}</div>
                        <div className="flex justify-between items-center text-slate-700 font-medium">
                          <span className="font-semibold text-slate-900">₹{p.price.toFixed(2)}</span>
                          <span className="text-[11px] text-slate-500">Margin: {p.margin_pct ?? 20}% | Stock: {p.inventory_count ?? 50}u</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setShowSearchModal(false)}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium"
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
