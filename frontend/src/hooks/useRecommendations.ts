import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { RecommendationItem, RecommendationMode } from '../types';

export const useRecommendations = (userId: number | null, mode: RecommendationMode) => {
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;

    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.get('/recommendations', {
          params: { user_id: userId, mode, limit: 12 },
        });
        if (response.data?.recommendations) {
          setRecommendations(response.data.recommendations);
        } else {
          setRecommendations([]);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [userId, mode]);

  return { recommendations, loading, error };
};
