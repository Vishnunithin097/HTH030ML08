import React, { useState, useEffect } from 'react';
import { RecommendationMode, RecommendationItem, User } from '../types';
import { useRecommendations } from '../hooks/useRecommendations';
import { ModeToggle } from '../components/ModeToggle';
import { RecommendationList } from '../components/RecommendationList';
import { WhyRecommendedModal } from '../components/WhyRecommendedModal';
import { apiClient } from '../api/client';
import { UserCheck, Sparkles } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [selectedUserId, setSelectedUserId] = useState<number>(999999999);
  const [users, setUsers] = useState<User[]>([]);
  const [mode, setMode] = useState<RecommendationMode>('business_aware');
  const [activeModalItem, setActiveModalItem] = useState<RecommendationItem | null>(null);

  const { recommendations, loading } = useRecommendations(selectedUserId, mode);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await apiClient.get('/users?limit=10');
      setUsers(res.data);
      if (res.data.length > 0 && !selectedUserId) {
        setSelectedUserId(res.data[0].user_id);
      }
    } catch (e) {
      console.error('Failed to fetch user list:', e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Controls Bar */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Live Recommendation Feed</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Compare pure machine learning relevance rankings against business guardrail re-rankings in real time.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 text-xs">
            <UserCheck className="w-4 h-4 text-slate-500" />
            <span className="font-semibold text-slate-700">Shopper:</span>
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(Number(e.target.value))}
              className="bg-transparent font-medium text-slate-900 focus:outline-none cursor-pointer"
            >
              <option value={999999999}>Demo Cold User (#999999999)</option>
              {users.map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  User #{u.user_id} {u.is_synthetic_cold_demo ? '(Cold Persona)' : ''}
                </option>
              ))}
            </select>
          </div>

          <ModeToggle mode={mode} onChange={setMode} />
        </div>
      </div>

      {/* Product Recommendation Slate */}
      <RecommendationList
        items={recommendations}
        loading={loading}
        onExplainClick={(item) => setActiveModalItem(item)}
      />

      {/* Explainability Audit Modal */}
      <WhyRecommendedModal
        item={activeModalItem}
        onClose={() => setActiveModalItem(null)}
      />
    </div>
  );
};
