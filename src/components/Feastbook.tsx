import React, { useState } from 'react';
import { Heart, Search, Clock, Utensils, Trash2, ChefHat, Sparkles } from 'lucide-react';
import { Recipe } from '../types';

interface FeastbookProps {
  savedRecipes: Recipe[];
  onOpenRecipe: (recipe: Recipe) => void;
  onRemoveFavorite: (id: string) => void;
}

export const Feastbook: React.FC<FeastbookProps> = ({ savedRecipes = [], onOpenRecipe, onRemoveFavorite }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'all' | 'favorites' | 'history'>('all');

  const filtered = (savedRecipes || []).filter(
    (r) =>
      r &&
      r.title &&
      (r.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (r.cuisine && r.cuisine.toLowerCase().includes(searchTerm.toLowerCase())))
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-4">
      {/* 21. TITLE HEADER */}
      <div className="text-center space-y-2">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-extrabold rounded-full">
          <Heart className="w-3.5 h-3.5 text-amber-400 fill-current" />
          Cookbook & History
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          ❤️ Feastbook
        </h1>
        <p className="text-slate-300 text-sm max-w-xl mx-auto">
          "Your saved recipes and kitchen history."
        </p>
      </div>

      {/* FILTER TABS */}
      <div className="flex justify-center gap-2">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all ${
            activeTab === 'all'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          Saved Recipes ({savedRecipes.length})
        </button>
        <button
          onClick={() => setActiveTab('favorites')}
          className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all ${
            activeTab === 'favorites'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          Favorites
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all ${
            activeTab === 'history'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          Cooking History
        </button>
      </div>

      {savedRecipes.length === 0 ? (
        <div className="bg-slate-900 rounded-3xl border border-slate-800 p-12 text-center space-y-4 max-w-lg mx-auto shadow-xl">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center mx-auto border border-amber-500/20">
            <Heart className="w-8 h-8 fill-current" />
          </div>
          <h3 className="font-black text-xl text-white">Your Feastbook is Empty</h3>
          <p className="text-slate-400 text-xs leading-relaxed">
            When you view recipes, click the heart icon on any recipe to save it here for quick cooking anytime.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* SEARCH BAR */}
          <div className="max-w-md mx-auto relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search saved recipes by title or cuisine..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-2xl pl-9 pr-4 py-2.5 text-xs font-bold text-white outline-none focus:border-emerald-500 shadow-md"
            />
          </div>

          {/* CARDS GRID */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((recipe) => (
              <div
                key={recipe.id}
                className="bg-slate-900 rounded-3xl border border-slate-800 p-6 shadow-xl hover:border-emerald-500/40 transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {recipe.cuisine}
                    </span>

                    <button
                      onClick={() => onRemoveFavorite(recipe.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
                      title="Remove from Feastbook"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h3 className="font-black text-white text-lg line-clamp-2 leading-snug">
                    {recipe.title}
                  </h3>

                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-300 pt-2 border-t border-slate-800">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{recipe.cooking_time_minutes} mins</span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <Utensils className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{recipe.servings} Servings</span>
                    </div>

                    <div className="flex items-center gap-1.5 font-bold text-emerald-400 col-span-2">
                      <span>♻️ {recipe.ingredient_utilization_percentage}% Utilization</span>
                    </div>
                  </div>

                  <div className="text-[10px] text-slate-400 font-bold">
                    Additional Cost: {recipe.estimated_missing_cost_inr === 0 ? '₹0' : `₹${recipe.estimated_missing_cost_inr}`}
                  </div>
                </div>

                <button
                  onClick={() => onOpenRecipe(recipe)}
                  className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl flex items-center justify-center gap-2 shadow-md transition-colors"
                >
                  <ChefHat className="w-4 h-4" />
                  <span>🍳 Cook Again</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
