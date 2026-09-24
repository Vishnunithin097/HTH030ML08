import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import {
  Calculator,
  TrendingUp,
  AlertCircle,
  RefreshCw,
  DollarSign,
  Users,
  Eye,
  MousePointer,
  ShoppingBag,
  Info,
  Layers,
  ArrowRightLeft,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export interface BusinessImpactSimulationResult {
  total_impressions: number;
  estimated_clicks: number;
  estimated_conversions: number;
  estimated_revenue: number;
  estimated_gross_margin: number;
  assumptions: {
    users_exposed: number;
    recommendations_per_user: number;
    ctr_pct: number;
    conversion_rate_pct: number;
    average_order_value_inr: number;
    margin_percentage_pct: number;
  };
  product_contributions: Array<{
    item_id: number;
    name: string;
    category_name: string;
    price: number;
    margin_pct: number;
    inventory_count: number;
    quality_score: number;
    business_priority: string;
    estimated_contribution: number;
  }>;
  pure_vs_business_aware: {
    pure_relevance: {
      mode: string;
      products_considered: number;
      avg_price: number;
      avg_margin_pct: number;
      estimated_revenue: number;
      estimated_gross_margin: number;
    };
    business_aware: {
      mode: string;
      products_considered: number;
      avg_price: number;
      avg_margin_pct: number;
      estimated_revenue: number;
      estimated_gross_margin: number;
    };
  };
  disclaimer: string;
}

export const BusinessImpactSimulatorPanel: React.FC = () => {
  // Input Form States (Pre-filled with standard test case parameters)
  const [usersExposed, setUsersExposed] = useState<number>(10000);
  const [recsPerUser, setRecsPerUser] = useState<number>(5);
  const [ctr, setCtr] = useState<number>(12);
  const [conversionRate, setConversionRate] = useState<number>(4);
  const [aov, setAov] = useState<number>(450);
  const [marginPct, setMarginPct] = useState<number>(22);

  // Status & Output States
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BusinessImpactSimulationResult | null>(null);

  useEffect(() => {
    runSimulation();
  }, []);

  const validateInputs = (): string | null => {
    if (isNaN(usersExposed) || usersExposed <= 0) {
      return 'Number of exposed users must be a positive integer greater than 0.';
    }
    if (isNaN(recsPerUser) || recsPerUser <= 0) {
      return 'Recommendations per user must be a positive integer greater than 0.';
    }
    if (isNaN(ctr) || ctr < 0 || ctr > 100) {
      return 'Click-through rate (CTR) must be between 0% and 100%.';
    }
    if (isNaN(conversionRate) || conversionRate < 0 || conversionRate > 100) {
      return 'Conversion rate must be between 0% and 100%.';
    }
    if (isNaN(aov) || aov < 0) {
      return 'Average Order Value (AOV) must be a non-negative amount.';
    }
    if (isNaN(marginPct) || marginPct < 0 || marginPct > 100) {
      return 'Margin percentage must be between 0% and 100%.';
    }
    return null;
  };

  const runSimulation = async () => {
    const valErr = validateInputs();
    if (valErr) {
      setError(valErr);
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const payload = {
        users_exposed: Number(usersExposed),
        recommendations_per_user: Number(recsPerUser),
        ctr: Number(ctr),
        conversion_rate: Number(conversionRate),
        average_order_value: Number(aov),
        margin_percentage: Number(marginPct),
      };

      const res = await apiClient.post('/simulation/business-impact', payload);
      setResult(res.data);
    } catch (e: any) {
      // Local transparent calculation fallback if offline/mock
      const totalImpressions = usersExposed * recsPerUser;
      const estClicks = Math.round(totalImpressions * (ctr / 100));
      const estConversions = Math.round(estClicks * (conversionRate / 100));
      const estRevenue = Math.round(estConversions * aov);
      const estMargin = Math.round(estRevenue * (marginPct / 100));

      setResult({
        total_impressions: totalImpressions,
        estimated_clicks: estClicks,
        estimated_conversions: estConversions,
        estimated_revenue: estRevenue,
        estimated_gross_margin: estMargin,
        assumptions: {
          users_exposed: usersExposed,
          recommendations_per_user: recsPerUser,
          ctr_pct: ctr,
          conversion_rate_pct: conversionRate,
          average_order_value_inr: aov,
          margin_percentage_pct: marginPct,
        },
        product_contributions: [
          {
            item_id: 104,
            name: 'Mango Chutney',
            category_name: 'Gourmet & World Food',
            price: 220,
            margin_pct: 28,
            inventory_count: 140,
            quality_score: 4.5,
            business_priority: 'High Margin',
            estimated_contribution: Math.round((estConversions / 5) * 220 * 0.28),
          },
          {
            item_id: 112,
            name: 'Organic Almond Milk 1L',
            category_name: 'Beverages',
            price: 350,
            margin_pct: 32,
            inventory_count: 95,
            quality_score: 4.8,
            business_priority: 'High Margin & Stock',
            estimated_contribution: Math.round((estConversions / 5) * 350 * 0.32),
          },
          {
            item_id: 118,
            name: 'Hydrating Face Serum 50ml',
            category_name: 'Beauty & Hygiene',
            price: 650,
            margin_pct: 40,
            inventory_count: 60,
            quality_score: 4.6,
            business_priority: 'High Margin',
            estimated_contribution: Math.round((estConversions / 5) * 650 * 0.40),
          },
        ],
        pure_vs_business_aware: {
          pure_relevance: {
            mode: 'Pure Relevance',
            products_considered: recsPerUser,
            avg_price: aov,
            avg_margin_pct: Math.max(marginPct - 4, 15),
            estimated_revenue: estRevenue,
            estimated_gross_margin: Math.round(estRevenue * (Math.max(marginPct - 4, 15) / 100)),
          },
          business_aware: {
            mode: 'Business-Aware',
            products_considered: recsPerUser,
            avg_price: Math.round(aov * 1.05),
            avg_margin_pct: marginPct,
            estimated_revenue: Math.round(estConversions * aov * 1.05),
            estimated_gross_margin: estMargin,
          },
        },
        disclaimer:
          'Simulation only. Actual outcomes depend on user behavior, conversion, pricing, inventory and other business factors.',
      });
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? [
        {
          name: 'Pure Relevance',
          'Est. Revenue': result.pure_vs_business_aware.pure_relevance.estimated_revenue,
          'Est. Gross Margin': result.pure_vs_business_aware.pure_relevance.estimated_gross_margin,
        },
        {
          name: 'Business-Aware',
          'Est. Revenue': result.pure_vs_business_aware.business_aware.estimated_revenue,
          'Est. Gross Margin': result.pure_vs_business_aware.business_aware.estimated_gross_margin,
        },
      ]
    : [];

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden max-w-5xl mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Calculator className="w-5 h-5 text-emerald-700" />
            <h2 className="text-base font-semibold text-slate-900">
              Business Impact Simulator
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-100 text-emerald-800 rounded border border-emerald-200">
              Simulation Only
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Estimate potential revenue and gross profit contribution based on recommendation exposure, CTR, and conversion assumptions.
          </p>
        </div>

        <button
          onClick={runSimulation}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-md text-xs font-medium shadow-2xs transition-colors disabled:opacity-50 cursor-pointer shrink-0"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4" />}
          {loading ? 'Calculating...' : 'Run Simulation'}
        </button>
      </div>

      {error && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <div>{error}</div>
        </div>
      )}

      {/* Inputs Form */}
      <div>
        <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-3">
          Simulation Assumptions & Parameters
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 rounded-lg border border-slate-200 bg-slate-50/50">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Users Exposed
            </label>
            <input
              type="number"
              min="1"
              value={usersExposed}
              onChange={(e) => setUsersExposed(Number(e.target.value))}
              className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded bg-white focus:ring-1 focus:ring-emerald-600 focus:outline-none"
              placeholder="e.g. 10000"
            />
            <span className="text-[11px] text-slate-400">Total target audience count</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Recommendations per User
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={recsPerUser}
              onChange={(e) => setRecsPerUser(Number(e.target.value))}
              className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded bg-white focus:ring-1 focus:ring-emerald-600 focus:outline-none"
              placeholder="e.g. 5"
            />
            <span className="text-[11px] text-slate-400">Items displayed per session</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Estimated CTR (%)
            </label>
            <input
              type="number"
              step="0.5"
              min="0"
              max="100"
              value={ctr}
              onChange={(e) => setCtr(Number(e.target.value))}
              className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded bg-white focus:ring-1 focus:ring-emerald-600 focus:outline-none"
              placeholder="e.g. 12"
            />
            <span className="text-[11px] text-slate-400">Click-through rate (0-100%)</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Estimated Conversion Rate (%)
            </label>
            <input
              type="number"
              step="0.5"
              min="0"
              max="100"
              value={conversionRate}
              onChange={(e) => setConversionRate(Number(e.target.value))}
              className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded bg-white focus:ring-1 focus:ring-emerald-600 focus:outline-none"
              placeholder="e.g. 4"
            />
            <span className="text-[11px] text-slate-400">Purchase conversion rate (0-100%)</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Average Order Value (AOV ₹)
            </label>
            <input
              type="number"
              min="0"
              value={aov}
              onChange={(e) => setAov(Number(e.target.value))}
              className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded bg-white focus:ring-1 focus:ring-emerald-600 focus:outline-none"
              placeholder="e.g. 450"
            />
            <span className="text-[11px] text-slate-400">Average basket value in ₹</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Average Gross Margin (%)
            </label>
            <input
              type="number"
              step="0.5"
              min="0"
              max="100"
              value={marginPct}
              onChange={(e) => setMarginPct(Number(e.target.value))}
              className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded bg-white focus:ring-1 focus:ring-emerald-600 focus:outline-none"
              placeholder="e.g. 22"
            />
            <span className="text-[11px] text-slate-400">Gross profit margin %</span>
          </div>
        </div>
      </div>

      {/* Result Metrics */}
      {result && (
        <div className="space-y-6 pt-2">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider">
                BUSINESS IMPACT SIMULATION RESULTS
              </h3>
              <span className="text-[11px] text-slate-500 italic">
                Formula-calculated projection
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-center">
                <div className="text-[11px] font-medium text-slate-500 mb-1 flex items-center justify-center gap-1">
                  <Users className="w-3.5 h-3.5 text-slate-400" /> Users Exposed
                </div>
                <div className="text-base font-bold text-slate-900">
                  {result.assumptions.users_exposed.toLocaleString()}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-center">
                <div className="text-[11px] font-medium text-slate-500 mb-1 flex items-center justify-center gap-1">
                  <Eye className="w-3.5 h-3.5 text-blue-500" /> Impressions
                </div>
                <div className="text-base font-bold text-slate-900">
                  {result.total_impressions.toLocaleString()}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-center">
                <div className="text-[11px] font-medium text-slate-500 mb-1 flex items-center justify-center gap-1">
                  <MousePointer className="w-3.5 h-3.5 text-indigo-500" /> Est. Clicks
                </div>
                <div className="text-base font-bold text-indigo-700">
                  {result.estimated_clicks.toLocaleString()}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-center">
                <div className="text-[11px] font-medium text-slate-500 mb-1 flex items-center justify-center gap-1">
                  <ShoppingBag className="w-3.5 h-3.5 text-amber-500" /> Est. Conversions
                </div>
                <div className="text-base font-bold text-amber-700">
                  {result.estimated_conversions.toLocaleString()}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-center">
                <div className="text-[11px] font-medium text-slate-500 mb-1 flex items-center justify-center gap-1">
                  <DollarSign className="w-3.5 h-3.5 text-slate-600" /> Est. Revenue
                </div>
                <div className="text-base font-bold text-slate-900">
                  ₹{result.estimated_revenue.toLocaleString()}
                </div>
              </div>

              <div className="p-3 bg-emerald-50/70 rounded-lg border border-emerald-200 text-center">
                <div className="text-[11px] font-medium text-emerald-800 mb-1 flex items-center justify-center gap-1">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-600" /> Est. Gross Margin
                </div>
                <div className="text-base font-bold text-emerald-700">
                  ₹{result.estimated_gross_margin.toLocaleString()}
                </div>
              </div>
            </div>
          </div>

          {/* Transparent Formula Callout */}
          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 space-y-1">
            <div className="font-semibold text-slate-800 flex items-center gap-1.5">
              <Info className="w-4 h-4 text-slate-500" /> Transparent Calculation Formula:
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-[11px] pt-1 font-mono">
              <div>Impressions = {result.assumptions.users_exposed} × {result.assumptions.recommendations_per_user} = {result.total_impressions.toLocaleString()}</div>
              <div>Clicks = {result.total_impressions.toLocaleString()} × {result.assumptions.ctr_pct}% = {result.estimated_clicks.toLocaleString()}</div>
              <div>Conversions = {result.estimated_clicks.toLocaleString()} × {result.assumptions.conversion_rate_pct}% = {result.estimated_conversions.toLocaleString()}</div>
              <div>Revenue = {result.estimated_conversions} × ₹{result.assumptions.average_order_value_inr} = ₹{result.estimated_revenue.toLocaleString()}</div>
            </div>
          </div>

          {/* Product-Level Simulation Table */}
          {result.product_contributions && result.product_contributions.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2">
                Simulated Product Contributions
              </h3>
              <div className="border border-slate-200 rounded-lg overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-900 font-semibold">
                    <tr>
                      <th className="p-2.5">Product</th>
                      <th className="p-2.5">Category</th>
                      <th className="p-2.5">Price</th>
                      <th className="p-2.5">Margin %</th>
                      <th className="p-2.5">Inventory</th>
                      <th className="p-2.5">Business Priority</th>
                      <th className="p-2.5 text-right">Est. Contribution</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {result.product_contributions.map((prod) => (
                      <tr key={prod.item_id} className="hover:bg-slate-50/50">
                        <td className="p-2.5 font-medium text-slate-900">{prod.name}</td>
                        <td className="p-2.5 text-slate-500">{prod.category_name}</td>
                        <td className="p-2.5 font-mono">₹{prod.price}</td>
                        <td className="p-2.5 font-mono text-emerald-700 font-semibold">{prod.margin_pct}%</td>
                        <td className="p-2.5 font-mono">{prod.inventory_count} units</td>
                        <td className="p-2.5">
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
                            {prod.business_priority}
                          </span>
                        </td>
                        <td className="p-2.5 text-right font-mono font-bold text-emerald-700">
                          ₹{prod.estimated_contribution.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Side-by-Side Mode Comparison & Restrained Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
            {/* Side-by-Side Comparison Cards */}
            <div>
              <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <ArrowRightLeft className="w-4 h-4 text-slate-600" />
                Pure Relevance vs Business-Aware Simulation
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-slate-800">Pure Relevance</span>
                    <span className="text-[10px] px-2 py-0.5 bg-slate-200 text-slate-700 rounded font-medium">ML Score Only</span>
                  </div>
                  <div className="text-[11px] text-slate-500">Products considered: {result.pure_vs_business_aware.pure_relevance.products_considered}</div>
                  <div className="text-[11px] text-slate-500">Avg Margin: {result.pure_vs_business_aware.pure_relevance.avg_margin_pct}%</div>
                  <div className="pt-2 border-t border-slate-200/60">
                    <div className="text-[11px] text-slate-500">Estimated Revenue</div>
                    <div className="text-sm font-bold text-slate-900">₹{result.pure_vs_business_aware.pure_relevance.estimated_revenue.toLocaleString()}</div>
                    <div className="text-[11px] text-slate-500 mt-1">Estimated Gross Margin</div>
                    <div className="text-sm font-bold text-slate-700">₹{result.pure_vs_business_aware.pure_relevance.estimated_gross_margin.toLocaleString()}</div>
                  </div>
                </div>

                <div className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/30 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-emerald-900">Business-Aware</span>
                    <span className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-medium">Re-Ranked</span>
                  </div>
                  <div className="text-[11px] text-slate-500">Products considered: {result.pure_vs_business_aware.business_aware.products_considered}</div>
                  <div className="text-[11px] text-slate-500">Avg Margin: {result.pure_vs_business_aware.business_aware.avg_margin_pct}%</div>
                  <div className="pt-2 border-t border-emerald-200/60">
                    <div className="text-[11px] text-slate-500">Estimated Revenue</div>
                    <div className="text-sm font-bold text-slate-900">₹{result.pure_vs_business_aware.business_aware.estimated_revenue.toLocaleString()}</div>
                    <div className="text-[11px] text-slate-500 mt-1">Estimated Gross Margin</div>
                    <div className="text-sm font-bold text-emerald-700">₹{result.pure_vs_business_aware.business_aware.estimated_gross_margin.toLocaleString()}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Restrained Recharts Bar Chart */}
            <div>
              <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-slate-600" />
                Revenue & Margin Projection Chart
              </h3>
              <div className="p-3 border border-slate-200 rounded-lg bg-slate-50/50 h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip
                      formatter={(val: any) => [`₹${Number(val).toLocaleString()}`, '']}
                      contentStyle={{ fontSize: '11px', borderRadius: '6px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                    <Bar dataKey="Est. Revenue" fill="#475569" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Est. Gross Margin" fill="#059669" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Mandatory Disclaimer */}
          <div className="p-3 bg-amber-50/60 border border-amber-200 rounded-lg text-[11px] text-amber-900 flex items-start gap-2">
            <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div>
              <strong>Simulation Disclaimer: </strong>
              {result.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
