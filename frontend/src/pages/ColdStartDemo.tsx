import React, { useState } from 'react';
import { apiClient } from '../api/client';
import { UserPlus, PackagePlus, Sparkles, Check } from 'lucide-react';

export const ColdStartDemo: React.FC = () => {
  const [userCategories, setUserCategories] = useState<string>('Beauty & Hygiene, Beverages');
  const [createdUser, setCreatedUser] = useState<any>(null);
  const [itemName, setItemName] = useState<string>('Organic Herbal Green Tea 100g');
  const [itemCategory, setItemCategory] = useState<string>('Beverages');
  const [itemPrice, setItemPrice] = useState<number>(349.0);
  const [createdItem, setCreatedItem] = useState<any>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleCreateColdUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const cats = userCategories.split(',').map((c) => c.trim()).filter(Boolean);
      const res = await apiClient.post('/demo/cold-start/user', {
        selected_categories: cats,
      });
      setCreatedUser(res.data);
      setStatusMsg(`Created cold user #${res.data.user_id}`);
    } catch (err: any) {
      alert(err.message || 'Error creating cold user');
    }
  };

  const handleCreateColdItem = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiClient.post('/demo/cold-start/item', {
        name: itemName,
        category_name: itemCategory,
        price: itemPrice,
        margin_pct: 35.0,
        inventory_count: 150,
        quality_score: 0.85,
        business_priority: 0.70,
        tags: ['organic', 'tea', 'herbal'],
      });
      setCreatedItem(res.data);
      setStatusMsg(`Created cold item #${res.data.item_id}`);
    } catch (err: any) {
      alert(err.message || 'Error creating cold item');
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-5 h-5 text-amber-500" />
          <h2 className="text-lg font-bold text-slate-900">Cold-Start Interactive Playground</h2>
        </div>
        <p className="text-xs text-slate-500">
          Simulate brand-new users (0 interaction logs) and brand-new catalog items to evaluate cold-start fallback resolvers.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Cold User Generator */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <UserPlus className="w-5 h-5 text-emerald-600" />
            <h3 className="text-sm font-bold text-slate-900">Simulate Cold-Start Shopper Persona</h3>
          </div>
          <form onSubmit={handleCreateColdUser} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Preferred Categories (comma-separated)
              </label>
              <input
                type="text"
                value={userCategories}
                onChange={(e) => setUserCategories(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2 bg-emerald-600 text-white rounded-xl text-xs font-semibold hover:bg-emerald-700 transition-colors"
            >
              Spawn Cold User
            </button>
          </form>

          {createdUser && (
            <div className="mt-4 p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-xs">
              <span className="font-bold text-emerald-900 block">User Created!</span>
              <p className="text-emerald-700">ID: #{createdUser.user_id}</p>
              <p className="text-emerald-700">Categories: {createdUser.selected_categories?.join(', ')}</p>
            </div>
          )}
        </div>

        {/* Cold Item Generator */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <PackagePlus className="w-5 h-5 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">Simulate Cold-Start Catalog Item</h3>
          </div>
          <form onSubmit={handleCreateColdItem} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Product Name</label>
              <input
                type="text"
                value={itemName}
                onChange={(e) => setItemName(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
                <input
                  type="text"
                  value={itemCategory}
                  onChange={(e) => setItemCategory(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Price (₹)</label>
                <input
                  type="number"
                  value={itemPrice}
                  onChange={(e) => setItemPrice(Number(e.target.value))}
                  className="w-full px-3 py-2 text-xs border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full py-2 bg-blue-600 text-white rounded-xl text-xs font-semibold hover:bg-blue-700 transition-colors"
            >
              Inject Cold Item
            </button>
          </form>

          {createdItem && (
            <div className="mt-4 p-3 bg-blue-50 rounded-xl border border-blue-200 text-xs">
              <span className="font-bold text-blue-900 block">Item Injected!</span>
              <p className="text-blue-700">ID: #{createdItem.item_id} - {createdItem.name}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
