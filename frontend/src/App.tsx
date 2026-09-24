import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Dashboard } from './pages/Dashboard';
import { ColdStartDemo } from './pages/ColdStartDemo';
import { AdminLogin } from './pages/AdminLogin';
import { AdminConfig } from './pages/AdminConfig';
import { Analytics } from './pages/Analytics';
import { Sparkles, Sliders, BarChart3, Lock, LogOut, LayoutDashboard, ShoppingBag } from 'lucide-react';

const NavigationBar: React.FC = () => {
  const location = useLocation();
  const { isAuthenticated, logout, username } = useAuth();

  const navLinks = [
    { to: '/', label: 'Recommendations', icon: LayoutDashboard },
    { to: '/cold-start', label: 'Cold-Start Lab', icon: Sparkles },
    { to: '/analytics', label: 'Analytics & Lift', icon: BarChart3 },
    { to: '/admin/config', label: 'Guardrail Policy', icon: Sliders },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Store Brand & Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div className="w-8 h-8 bg-emerald-700 rounded-md flex items-center justify-center text-white font-bold text-sm shadow-2xs">
            <ShoppingBag className="w-4 h-4 text-emerald-100" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-semibold text-slate-900 tracking-tight">RecoGuard</span>
              <span className="text-[10px] font-medium bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">Storefront</span>
            </div>
            <p className="text-[11px] text-slate-500 font-normal hidden sm:block">Cold-Start Hybrid Recommendations with Business Guardrails</p>
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
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-100 text-slate-900 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-slate-900' : 'text-slate-400'}`} />
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
                className="flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md text-xs font-medium transition-colors cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign Out
              </button>
            </div>
          ) : (
            <Link
              to="/admin/login"
              className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium transition-colors shadow-2xs"
            >
              <Lock className="w-3.5 h-3.5 text-slate-300" />
              Admin Access
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
          <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
            RecoGuard • Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails
          </footer>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
