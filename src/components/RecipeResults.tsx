import React, { useState } from 'react';
import { Clock, Utensils, Heart, ArrowRight, ChevronDown, ChevronUp, Sparkles, ChefHat } from 'lucide-react';
import { Recipe } from '../types';

interface RecipeResultsProps {
  recipes: Recipe[];
  onSelectRecipe: (recipe: Recipe) => void;
  onSaveFavorite: (recipe: Recipe) => void;
  savedRecipeIds: string[];
  onStartScan?: () => void;
  onGoToKitchenAgent?: () => void;
}

export const RecipeResults: React.FC<RecipeResultsProps> = ({
  recipes = [],
  onSelectRecipe,
  onSaveFavorite,
  savedRecipeIds = [],
  onStartScan,
  onGoToKitchenAgent,
}) => {
  const [openWhyId, setOpenWhyId] = useState<string | null>(null);

  if (!recipes || recipes.length === 0) {
    return (
      <div className="max-w-md mx-auto my-16 bg-slate-900 rounded-2xl border border-slate-800 p-8 text-center space-y-4 shadow-xl">
        <h2 className="text-xl font-bold text-white">No recipes generated yet</h2>
        <p className="text-slate-400 text-xs leading-relaxed">
          Set your preferences in the Kitchen Agent or scan your fridge to craft tailored recipes.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          {onGoToKitchenAgent && (
            <button
              onClick={onGoToKitchenAgent}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors"
            >
              Open Kitchen Agent
            </button>
          )}
          {onStartScan && (
            <button
              onClick={onStartScan}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs rounded-xl border border-slate-700 transition-colors"
            >
              Scan fridge
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-4 px-4 sm:px-6">
      {/* SECTION TITLE & SUBTITLE */}
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Curated Suggestions</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Your Crafted Feasts
        </h1>
        <p className="text-slate-400 text-sm">
          3 personalized recipes optimized to maximize inventory use and flavor.
        </p>
      </div>

      {/* 3 RECIPE CARDS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {recipes.slice(0, 3).map((recipe, index) => {
          const isSaved = savedRecipeIds.includes(recipe.id);

          let badgeLabel = 'Best Match';
          let badgeStyle = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';

          if (index === 1 || recipe.badge === 'Quick Feast') {
            badgeLabel = 'Quick Feast';
            badgeStyle = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
          } else if (index === 2 || recipe.badge === 'Creative Pick') {
            badgeLabel = 'Creative Pick';
            badgeStyle = 'bg-purple-500/10 text-purple-400 border-purple-500/20';
          }

          const isWhyOpen = openWhyId === recipe.id;
          const missingCount = recipe.ingredients_missing?.length || recipe.missing_ingredients?.length || 0;

          return (
            <div
              key={recipe.id}
              className="bg-slate-900 rounded-2xl border border-slate-800 p-5 shadow-lg flex flex-col justify-between hover:border-slate-700 transition-all duration-200 relative"
            >
              <div className="space-y-4">
                {/* Header Badge & Save Button */}
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${badgeStyle}`}>
                    {badgeLabel}
                  </span>

                  <button
                    onClick={() => onSaveFavorite(recipe)}
                    className={`p-1.5 rounded-lg transition-colors ${
                      isSaved ? 'text-rose-400 bg-rose-950/40' : 'text-slate-400 hover:text-rose-400 hover:bg-slate-800'
                    }`}
                    title={isSaved ? 'Saved in Feastbook' : 'Save to Feastbook'}
                  >
                    <Heart className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
                  </button>
                </div>

                {/* Title & Description */}
                <div>
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    {recipe.cuisine} • {recipe.difficulty}
                  </div>
                  <h3 className="text-lg font-bold text-white mt-1 leading-snug">
                    {recipe.title}
                  </h3>
                  <p className="text-slate-400 text-xs mt-2 line-clamp-3 leading-relaxed">
                    {recipe.short_description}
                  </p>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-300 bg-slate-800/60 p-2 rounded-xl font-medium">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{recipe.cooking_time_minutes} mins</span>
                  </div>

                  <div className="flex items-center gap-1.5 text-slate-300 bg-slate-800/60 p-2 rounded-xl font-medium">
                    <Utensils className="w-3.5 h-3.5 text-slate-400" />
                    <span>{recipe.servings} Servings</span>
                  </div>

                  <div className="flex items-center justify-between text-xs text-emerald-400 bg-emerald-950/30 px-3 py-2 rounded-xl font-semibold col-span-2 border border-emerald-500/20">
                    <span>Utilization</span>
                    <span>{recipe.ingredient_utilization_percentage}% of inventory</span>
                  </div>
                </div>

                <div className="text-xs text-slate-400 font-medium">
                  {missingCount === 0 ? (
                    <span className="text-emerald-400">100% kitchen ready (no extra items)</span>
                  ) : (
                    <span>Needs {missingCount} pantry item{missingCount > 1 ? 's' : ''}</span>
                  )}
                </div>

                {/* WHY THIS RECIPE WON */}
                <div className="pt-1">
                  <button
                    onClick={() => setOpenWhyId(isWhyOpen ? null : recipe.id)}
                    className="w-full flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/50 px-3 py-2 rounded-xl border border-slate-700/40 transition-colors"
                  >
                    <span>Why this recipe won</span>
                    {isWhyOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {isWhyOpen && (
                    <div className="mt-2 p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300 space-y-1 leading-relaxed">
                      <p className="font-semibold text-emerald-400">
                        • Uses {recipe.ingredient_utilization_percentage}% of your tracked inventory.
                      </p>
                      <p>• Tailored for {recipe.cooking_time_minutes} minutes cooking time and {recipe.servings} servings.</p>
                      <p>• Prioritizes high-perishable vegetables in your fridge.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* PRIMARY CTA */}
              <div className="pt-4 border-t border-slate-800 mt-5">
                <button
                  onClick={() => onSelectRecipe(recipe)}
                  id={`cook-recipe-btn-${recipe.id}`}
                  className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-sm transition-colors"
                >
                  <ChefHat className="w-4 h-4" />
                  <span>Start cooking</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
