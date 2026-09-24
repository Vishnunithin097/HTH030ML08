import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { UserPlus, PackagePlus, Sparkles, CheckCircle2, ArrowRight, ShieldCheck, Cpu, Layers, HelpCircle } from 'lucide-react';

export const ColdStartDemo: React.FC = () => {
  const navigate = useNavigate();

  // Cold User Form State
  const [userCategories, setUserCategories] = useState<string>('Beauty & Hygiene, Gourmet & World Food');
  const [createdUser, setCreatedUser] = useState<any>(null);
  const [userLoading, setUserLoading] = useState<boolean>(false);

  // Cold Item Form State
  const [itemName, setItemName] = useState<string>('Organic Cold-Pressed Virgin Coconut Oil 500ml');
  const [itemCategory, setItemCategory] = useState<string>('Gourmet & World Food');
  const [itemPrice, setItemPrice] = useState<number>(420.0);
  const [itemMargin, setItemMargin] = useState<number>(38.0);
  const [itemInventory, setItemInventory] = useState<number>(120);
  const [createdItem, setCreatedItem] = useState<any>(null);
  const [itemLoading, setItemLoading] = useState<boolean>(false);

  const [notification, setNotification] = useState<string | null>(null);

  const handleCreateColdUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setUserLoading(true);
    setNotification(null);
    try {
      const cats = userCategories.split(',').map((c) => c.trim()).filter(Boolean);
      const res = await apiClient.post('/demo/cold-start/user', {
        selected_categories: cats,
      });
      setCreatedUser(res.data);
      setNotification(`Created cold-start shopper profile User #${res.data.user_id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create cold user.');
    } finally {
      setUserLoading(false);
    }
  };

  const handleCreateColdItem = async (e: React.FormEvent) => {
    e.preventDefault();
    setItemLoading(true);
    setNotification(null);
    try {
      const res = await apiClient.post('/demo/cold-start/item', {
        name: itemName,
        category_name: itemCategory,
        price: itemPrice,
        margin_pct: itemMargin,
        inventory_count: itemInventory,
        quality_score: 0.88,
        business_priority: 0.75,
        tags: ['organic', 'cold-pressed', 'pure', 'gourmet'],
      });
      setCreatedItem(res.data);
      setNotification(`Injected cold-start catalog item #${res.data.item_id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create cold item.');
    } finally {
      setItemLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-5 h-5 text-amber-500" />
          <h2 className="text-lg font-bold text-slate-900">Cold-Start Simulation & Resolution Lab</h2>
        </div>
        <p className="text-xs text-slate-500 max-w-3xl leading-relaxed">
          Simulate brand-new shoppers (zero interaction history) and newly introduced catalog products. Observe how our hybrid recommendation engine falls back gracefully from collaborative filtering to content-based category affinity profiling and heuristic business scoring without degrading user experience.
        </p>
      </div>

      {notification && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Two-Column Simulation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Cold-Start Shopper Persona Simulator */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                  <UserPlus className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Simulate Cold-Start Shopper</h3>
                  <span className="text-[10px] text-slate-400">Zero interaction log history</span>
                </div>
              </div>
              <span className="text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded">
                User Cold Start
              </span>
            </div>

            <form onSubmit={handleCreateColdUser} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Onboarding Preferred Categories (comma-separated)
                </label>
                <input
                  type="text"
                  value={userCategories}
                  onChange={(e) => setUserCategories(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                  placeholder="e.g. Beverages, Snacks & Branded Foods"
                  required
                />
                <p className="text-[10px] text-slate-400 mt-1">
                  Simulates category selections during new user registration/onboarding.
                </p>
              </div>

              <button
                type="submit"
                disabled={userLoading}
                className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
              >
                {userLoading ? 'Creating Persona...' : 'Generate Cold Shopper'}
              </button>
            </form>
          </div>

          {createdUser && (
            <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900">Created User #{createdUser.user_id}</span>
                <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                  Cold Persona Ready
                </span>
              </div>
              <p className="text-[11px] text-slate-600">
                Categories: <strong>{createdUser.selected_categories?.join(', ')}</strong>
              </p>
              <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-200/60">
                Fallback Strategy: Content TF-IDF vectorization against category catalog + popularity baseline.
              </div>
            </div>
          )}
        </div>

        {/* Cold-Start Catalog Item Simulator */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                  <PackagePlus className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Simulate Cold-Start Catalog Item</h3>
                  <span className="text-[10px] text-slate-400">Zero historical user interactions</span>
                </div>
              </div>
              <span className="text-[10px] font-bold bg-blue-50 text-blue-800 border border-blue-200 px-2 py-0.5 rounded">
                Item Cold Start
              </span>
            </div>

            <form onSubmit={handleCreateColdItem} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Product Title</label>
                <input
                  type="text"
                  value={itemName}
                  onChange={(e) => setItemName(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
                  <input
                    type="text"
                    value={itemCategory}
                    onChange={(e) => setItemCategory(e.target.value)}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Price (₹)</label>
                  <input
                    type="number"
                    value={itemPrice}
                    onChange={(e) => setItemPrice(Number(e.target.value))}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Margin (%)</label>
                  <input
                    type="number"
                    value={itemMargin}
                    onChange={(e) => setItemMargin(Number(e.target.value))}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Inventory (Units)</label>
                  <input
                    type="number"
                    value={itemInventory}
                    onChange={(e) => setItemInventory(Number(e.target.value))}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={itemLoading}
                className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
              >
                {itemLoading ? 'Injecting Item...' : 'Inject Cold Catalog Item'}
              </button>
            </form>
          </div>

          {createdItem && (
            <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900">Item #{createdItem.item_id} Injected</span>
                <span className="text-[10px] font-semibold bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                  TF-IDF Vectorized
                </span>
              </div>
              <p className="text-[11px] text-slate-600 line-clamp-1">{createdItem.name}</p>
              <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-200/60">
                Fallback Strategy: Content TF-IDF sparse similarity cosine scoring + business guardrail heuristic scoring.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Technical Architecture Reference Box */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
          Cold-Start Engine Fallback Topology
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 space-y-2">
            <div className="flex items-center gap-2 text-slate-900 font-bold">
              <Cpu className="w-4 h-4 text-blue-600" />
              <span>Shopper Cold-Start</span>
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              When user has &lt; 5 interactions, SVD collaborative latent factors are unavailable. Engine synthesizes a pseudo-profile from onboarding category selections and performs TF-IDF cosine ranking across 23,541 catalog products.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 space-y-2">
            <div className="flex items-center gap-2 text-slate-900 font-bold">
              <Layers className="w-4 h-4 text-emerald-600" />
              <span>Item Cold-Start</span>
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              When a new SKU enters the catalog without click/add-to-cart signals, content-based vector embeddings represent its text features. Business guardrails immediately evaluate profit margin and stock levels.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 space-y-2">
            <div className="flex items-center gap-2 text-slate-900 font-bold">
              <ShieldCheck className="w-4 h-4 text-purple-600" />
              <span>Dual Cold-Start</span>
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              When both shopper and items have zero interaction graph overlap, popularity-dampened category heuristics combined with inventory safety guardrails provide guaranteed candidate delivery with zero 500 errors.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
