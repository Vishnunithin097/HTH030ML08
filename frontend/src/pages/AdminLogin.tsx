import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../api/client';
import { Lock, AlertCircle, Info, KeyRound } from 'lucide-react';

export const AdminLogin: React.FC = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('Admin@123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await apiClient.post('/auth/login', { username, password });
      login(res.data.access_token, res.data.username);
      navigate('/admin/config');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-xl border border-slate-200 shadow-sm">
      <div className="text-center mb-6">
        <div className="w-10 h-10 bg-slate-100 text-slate-800 rounded-xl flex items-center justify-center mx-auto mb-3">
          <KeyRound className="w-5 h-5" />
        </div>
        <h2 className="text-base font-bold text-slate-900">Admin Control Center Authentication</h2>
        <p className="text-xs text-slate-500 mt-1">
          Sign in with administrator credentials to modify business guardrails and inventory thresholds.
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-rose-50 text-rose-800 rounded-lg text-xs flex items-center gap-2 border border-rose-200">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Admin Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition-colors disabled:opacity-50 cursor-pointer"
        >
          {loading ? 'Authenticating Admin...' : 'Sign In as Administrator'}
        </button>
      </form>

      <div className="mt-6 p-3 bg-slate-50 rounded-lg border border-slate-200/80 text-[11px] text-slate-500 flex items-start gap-2">
        <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-700">Evaluation Demo Credentials:</span>
          <div>Username: <code className="text-slate-800 font-mono">admin</code> | Password: <code className="text-slate-800 font-mono">Admin@123</code></div>
        </div>
      </div>
    </div>
  );
};
