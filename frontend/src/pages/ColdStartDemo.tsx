import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { UserPlus, PackagePlus, Sparkles, CheckCircle2, ArrowRight, ShieldCheck, Cpu, Layers } from 'lucide-react';

const POPULAR_CATEGORIES = [
  'Beauty & Hygiene',
  'Gourmet & World Food',
  'Beverages',
  'Snacks & Branded Foods',
  'Bakery, Cakes & Dairy',
  'Cleaning & Household',
  'Foodgrains, Oil & Masala',
];

export const ColdStartDemo: React.FC = () => {
  const navigate = useNavigate();

  // Cold User Form State
  const [selectedCats, setSelectedCats] = useState<string[]>(['Beauty & Hygiene', 'Gourmet & World Food']);
  const [customCat, setCustomCat] = useState<string>('');
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

  const toggleCategory = (cat: string) => {
    setSelectedCats((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  };

  const handleAddCustomCat = () => {
    if (customCat.trim() && !selectedCats.includes(customCat.trim())) {
      setSelectedCats([...selectedCats, customCat.trim()]);
      setCustomCat('');
    }
  };

  const handleCreateColdUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedCats.length === 0) {
      alert('Please select at least one onboarding category.');
      return;
    }
    setUserLoading(true);
    setNotification(null);
    try {
      const res = await apiClient.post('/demo/cold-start/user', {
        selected_categories: selectedCats,
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
      setNotification(`Injected cold-start catalog item SKU #${res.data.item_id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create cold item.');
    } finally {
      setItemLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex items-center gap-2 mb-1.5">
          <Sparkles className="w-5 h-5 text-amber-500" />
          <h1 className="text-lg font-semibold text-slate-900">Cold-Start Simulation & Resolution Lab</h1>
        </div>
        <p className="text-xs text-slate-500 max-w-3xl leading-relaxed">
          Simulate brand-new shoppers (zero interaction history) and newly introduced catalog products. Observe how the hybrid recommendation engine falls back gracefully from SVD collaborative filtering to TF-IDF content similarity and category affinity profiling without generating errors.
        </p>
      </div>

      {notification && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 font-medium flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{notification}</span>
          </div>
          {createdUser && (
            <button
              onClick={() => navigate('/')}
              className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-800 underline hover:text-emerald-950"
            >
              View Shopper Feed <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Two-Column Simulation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Cold-Start Shopper Persona Simulator */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center font-semibold">
                  <UserPlus className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Simulate Cold-Start Shopper</h3>
                  <span className="text-[11px] text-slate-400">Zero interaction transaction history</span>
                </div>
              </div>
              <span className="text-[10px] font-medium bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded">
                User Cold Start
              </span>
            </div>

            <form onSubmit={handleCreateColdUser} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-2">
                  Select Onboarding Categories
                </label>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {POPULAR_CATEGORIES.map((cat) => {
                    const active = selectedCats.includes(cat);
                    return (
                      <button
                        key={cat}
                        type="button"
                        onClick={() => toggleCategory(cat)}
                        className={`px-2.5 py-1 rounded text-xs font-medium border transition-all ${
                          active
                            ? 'bg-emerald-700 text-white border-emerald-700 shadow-2xs'
                            : 'bg-slate-50 text-slate-600 border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        {cat}
                      </button>
                    );
                  })}
                </div>

                <div className="flex gap-1.5 mt-2">
                  <input
                    type="text"
                    value={customCat}
                    onChange={(e) => setCustomCat(e.target.value)}
                    placeholder="Add custom category..."
                    className="flex-1 px-2.5 py-1 text-xs border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-emerald-600"
                  />
                  <button
                    type="button"
                    onClick={handleAddCustomCat}
                    className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-medium"
                  >
                    Add
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={userLoading}
                className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium transition-colors disabled:opacity-50"
              >
                {userLoading ? 'Creating Persona...' : 'Generate Cold Shopper'}
              </button>
            </form>
          </div>

          {createdUser && (
            <div className="mt-4 p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-900">Shopper #{createdUser.user_id}</span>
                <span className="text-[10px] font-medium bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                  Cold Profile Ready
                </span>
              </div>
              <p className="text-xs text-slate-600">
                Affinities: <strong>{createdUser.selected_categories?.join(', ')}</strong>
              </p>
              <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-200/80">
                Resolution: Content TF-IDF vectorization against stated categories + popularity baseline.
              </div>
            </div>
          )}
        </div>

        {/* Cold-Start Catalog Item Simulator */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center font-semibold">
                  <PackagePlus className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Simulate Cold-Start Catalog Item</h3>
                  <span className="text-[11px] text-slate-400">Zero historical user interactions</span>
                </div>
              </div>
              <span className="text-[10px] font-medium bg-blue-50 text-blue-800 border border-blue-200 px-2 py-0.5 rounded">
                Item Cold Start
              </span>
            </div>

            <form onSubmit={handleCreateColdItem} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Product Title</label>
                <input
                  type="text"
                  value={itemName}
                  onChange={(e) => setItemName(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-900 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Category</label>
                  <input
                    type="text"
                    value={itemCategory}
                    onChange={(e) => setItemCategory(e.target.value)}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Price (₹)</label>
                  <input
                    type="number"
                    value={itemPrice}
                    onChange={(e) => setItemPrice(Number(e.target.value))}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Margin (%)</label>
                  <input
                    type="number"
                    value={itemMargin}
                    onChange={(e) => setItemMargin(Number(e.target.value))}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Inventory (Units)</label>
                  <input
                    type="number"
                    value={itemInventory}
                    onChange={(e) => setItemInventory(Number(e.target.value))}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-900 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={itemLoading}
                className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium transition-colors disabled:opacity-50"
              >
                {itemLoading ? 'Injecting SKU...' : 'Inject Cold Catalog Item'}
              </button>
            </form>
          </div>

          {createdItem && (
            <div className="mt-4 p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-900">SKU #{createdItem.item_id} Ingested</span>
                <span className="text-[10px] font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                  TF-IDF Vectorized
                </span>
              </div>
              <p className="text-xs text-slate-600 line-clamp-1">{createdItem.name}</p>
              <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-200/80">
                Resolution: Real-time text embedding projection + immediate business guardrail eligibility.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Technical Architecture Reference Box */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <h4 className="text-xs font-semibold text-slate-900 mb-3">
          Cold-Start Resolution Strategy Topology
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/60 space-y-1.5">
            <div className="flex items-center gap-2 text-slate-900 font-semibold">
              <Cpu className="w-4 h-4 text-blue-600" />
              <span>Shopper Cold-Start</span>
            </div>
            <p className="text-slate-500 text-xs leading-relaxed">
              When user has &lt; 5 interactions, SVD collaborative latent factors are unavailable. Engine synthesizes a profile from onboarding category selections and performs TF-IDF cosine ranking.
            </p>
          </div>

          <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/60 space-y-1.5">
            <div className="flex items-center gap-2 text-slate-900 font-semibold">
              <Layers className="w-4 h-4 text-emerald-600" />
              <span>Item Cold-Start</span>
            </div>
            <p className="text-slate-500 text-xs leading-relaxed">
              When a new SKU enters the catalog without click/order signals, content-based vector embeddings represent its text features. Business guardrails immediately evaluate margin and stock levels.
            </p>
          </div>

          <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/60 space-y-1.5">
            <div className="flex items-center gap-2 text-slate-900 font-semibold">
              <ShieldCheck className="w-4 h-4 text-purple-600" />
              <span>Dual Cold-Start</span>
            </div>
            <p className="text-slate-500 text-xs leading-relaxed">
              When both shopper and items have zero interaction history, category affinity heuristics combined with inventory safety guardrails provide guaranteed candidate delivery with zero runtime errors.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
