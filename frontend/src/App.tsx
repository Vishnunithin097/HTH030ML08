import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Dashboard } from './pages/Dashboard';
import { ColdStartDemo } from './pages/ColdStartDemo';
import { AdminLogin } from './pages/AdminLogin';
import { AdminConfig } from './pages/AdminConfig';
import { Analytics } from './pages/Analytics';
import { Sparkles, Sliders, BarChart3, Lock, LogOut, LayoutDashboard, ShieldCheck } from 'lucide-react';

const NavigationBar: React.FC = () => {
  const location = useLocation();
  const { isAuthenticated, logout, username } = useAuth();

  const navLinks = [
    { to: '/', label: 'Recommendation Feed', icon: LayoutDashboard },
    { to: '/cold-start', label: 'Cold-Start Lab', icon: Sparkles },
    { to: '/analytics', label: 'Evaluation & Lift', icon: BarChart3 },
    { to: '/admin/config', label: 'Guardrail Controls', icon: Sliders },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-bold text-slate-900 tracking-tight">RecoGuard</span>
              <span className="text-[10px] font-semibold bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded border border-emerald-200">PROD</span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium">Recommendation Intelligence with Business Guardrails</p>
          </div>
        </Link>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  isActive
                    ? 'bg-slate-100 text-slate-900'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-slate-900' : 'text-slate-400'}`} />
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Auth / Admin Action */}
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-medium hidden sm:inline">
                Admin: <strong className="text-slate-900">{username}</strong>
              </span>
              <button
                onClick={logout}
                className="flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign Out
              </button>
            </div>
          ) : (
            <Link
              to="/admin/login"
              className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors shadow-sm"
            >
              <Lock className="w-3.5 h-3.5 text-slate-300" />
              Admin Portal
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
          <NavigationBar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/cold-start" element={<ColdStartDemo />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin/config" element={<AdminConfig />} />
            </Routes>
          </main>
          <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
            RecoGuard AI • Production Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails
          </footer>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
