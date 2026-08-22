import React, { useState } from 'react';
import { ChefHat, Camera, ListCheck, BookMarked, BarChart3, Sparkles, UtensilsCrossed, User, LogOut, UserPlus, ChevronDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export type NavTab = 'home' | 'scan' | 'review' | 'agent' | 'rescue' | 'recipes' | 'planner' | 'feastbook' | 'analytics';

interface NavbarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  confirmedCount: number;
  savedCount: number;
  hasRecipes: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  confirmedCount,
  savedCount,
  hasRecipes,
}) => {
  const { user, isGuest, logout, setCurrentAuthView } = useAuth();
  const [userMenuOpen, setUserMenuOpen] = useState<boolean>(false);

  return (
    <header className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 text-slate-100 shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 py-2">
          {/* Left: Brand Logo & Tagline */}
          <button
            onClick={() => setActiveTab('home')}
            className="flex items-center gap-3 text-left group focus:outline-none shrink-0"
            id="nav-brand-logo"
          >
            <div className="w-9 h-9 rounded-xl bg-emerald-600 flex items-center justify-center text-white font-bold shadow-md">
              <ChefHat className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight text-white group-hover:text-emerald-400 transition-colors">
                Fridge2Feast
              </span>
            </div>
          </button>

          {/* Primary Navigation Items */}
          <nav className="hidden lg:flex items-center gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('home')}
              id="nav-tab-home"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'home'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Dashboard
            </button>

            <button
              onClick={() => setActiveTab('scan')}
              id="nav-tab-scan"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'scan'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Scanner
            </button>

            <button
              onClick={() => setActiveTab('review')}
              id="nav-tab-inventory"
              className={`px-3 py-1.5 rounded-lg transition-colors relative ${
                activeTab === 'review'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              My Inventory
              {confirmedCount > 0 && (
                <span className="ml-1.5 text-[10px] px-1.5 py-0.5 bg-slate-800 text-emerald-400 font-bold rounded-full border border-slate-700">
                  {confirmedCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('agent')}
              id="nav-tab-agent"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'agent'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Kitchen Agent
            </button>

            <button
              onClick={() => setActiveTab('rescue')}
              id="nav-tab-rescue"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'rescue'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Rescue
            </button>

            <button
              onClick={() => setActiveTab('recipes')}
              id="nav-tab-recipes"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'recipes'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Recipes
            </button>

            <button
              onClick={() => setActiveTab('planner')}
              id="nav-tab-planner"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'planner'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Meal Planner
            </button>

            <button
              onClick={() => setActiveTab('feastbook')}
              id="nav-tab-feastbook"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'feastbook'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Feastbook
              {savedCount > 0 && (
                <span className="ml-1.5 text-[10px] px-1.5 py-0.5 bg-slate-800 text-amber-400 font-bold rounded-full border border-slate-700">
                  {savedCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              id="nav-tab-impact"
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'analytics'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Impact
            </button>
          </nav>

          {/* Right: User Avatar / Guest Badge & Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setActiveTab('scan')}
              id="nav-quick-scan-btn"
              className="hidden sm:flex px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-sm transition-all"
            >
              Scan fridge
            </button>

            {/* USER MENU DROPDOWN */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-2 transition-all ${
                  isGuest
                    ? 'bg-slate-800/80 text-amber-300 border-amber-800/50'
                    : 'bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700'
                }`}
              >
                <div className="w-5 h-5 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">
                  <User className="w-3 h-3" />
                </div>
                <span>{isGuest ? 'Guest' : (user?.name || 'Chef')}</span>
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </button>

              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-52 bg-slate-900 border border-slate-800 rounded-xl shadow-xl p-2 z-50 animate-fadeIn text-xs space-y-1">
                  <div className="px-3 py-2 border-b border-slate-800">
                    <p className="font-bold text-white">{user?.name || 'User'}</p>
                    <p className="text-[11px] text-slate-400 truncate">{user?.email || 'guest@fridge2feast.ai'}</p>
                  </div>

                  {isGuest && (
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        setCurrentAuthView('signup');
                      }}
                      className="w-full text-left px-3 py-2 rounded-lg text-emerald-400 hover:bg-emerald-950/40 font-semibold flex items-center gap-2"
                    >
                      <UserPlus className="w-3.5 h-3.5" />
                      <span>Create Account</span>
                    </button>
                  )}

                  <button
                    onClick={() => {
                      setUserMenuOpen(false);
                      logout();
                    }}
                    className="w-full text-left px-3 py-2 rounded-lg text-rose-400 hover:bg-rose-950/40 font-semibold flex items-center gap-2"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Log Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Navigation bar */}
        <div className="flex lg:hidden overflow-x-auto py-2 gap-1 border-t border-slate-800 scrollbar-none text-xs">
          <button
            onClick={() => setActiveTab('home')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'home' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('scan')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'scan' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Scanner
          </button>
          <button
            onClick={() => setActiveTab('review')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'review' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Inventory ({confirmedCount})
          </button>
          <button
            onClick={() => setActiveTab('agent')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'agent' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Agent
          </button>
          <button
            onClick={() => setActiveTab('rescue')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'rescue' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Rescue
          </button>
          <button
            onClick={() => setActiveTab('recipes')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'recipes' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Recipes
          </button>
          <button
            onClick={() => setActiveTab('planner')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'planner' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Planner
          </button>
          <button
            onClick={() => setActiveTab('feastbook')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'feastbook' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Feastbook ({savedCount})
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap ${
              activeTab === 'analytics' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Impact
          </button>
        </div>
      </div>
    </header>
  );
};
