import React from 'react';
import { Sparkles, Clock, Utensils, ChefHat, ArrowRight, CheckCircle2, Flame, Heart } from 'lucide-react';
import { Recipe } from '../types';
import { RecommendationCardData } from '../utils/recommendations';

interface RecommendedFeastsProps {
  recommendations: RecommendationCardData[];
  isFreshUser: boolean;
  onSelectRecipe: (recipe: Recipe) => void;
  onLoadIngredients?: (recipe: Recipe) => void;
  onSaveFavorite?: (recipe: Recipe) => void;
  savedRecipeIds?: string[];
}

export const RecommendedFeasts: React.FC<RecommendedFeastsProps> = ({
  recommendations = [],
  isFreshUser,
  onSelectRecipe,
  onLoadIngredients = (_r?: Recipe) => {},
  onSaveFavorite = (_r?: Recipe) => {},
  savedRecipeIds = [],
}) => {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <section className="space-y-5">
      {/* Header with clear user context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-extrabold border border-emerald-500/30 mb-1.5">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>{isFreshUser ? 'FRESH CHEF ESSENTIALS' : 'PERSONALIZED TASTE PROFILE'}</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">
            {isFreshUser ? '🌟 Recommended Everyday Feasts' : '🎯 Recommended Based on Your Previous Searches'}
          </h2>
          <p className="text-slate-400 text-xs sm:text-sm mt-0.5">
            {isFreshUser
              ? 'Wholesome, easy-to-cook staple meals with minimal pantry ingredients to get you cooking immediately.'
              : 'Tailored to your scanned vegetables, favored cuisines, and previous cooking history.'}
          </p>
        </div>
      </div>

      {/* Grid of Recommended Dishes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {recommendations.map((item) => {
          const recipe = item.recipe;
          const isSaved = savedRecipeIds.includes(recipe.id);

          return (
            <div
              key={item.id}
              className="bg-slate-900 rounded-3xl border border-slate-800 hover:border-emerald-500/50 p-6 flex flex-col justify-between shadow-xl transition-all duration-300 group relative"
            >
              <div className="space-y-4">
                {/* Top Badge & Rationale */}
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {item.badge}
                  </span>
                  <button
                    onClick={() => onSaveFavorite(recipe)}
                    className={`p-1.5 rounded-full transition-colors ${
                      isSaved ? 'text-rose-400 bg-rose-950/80' : 'text-slate-400 hover:text-rose-400 hover:bg-slate-800'
                    }`}
                    title={isSaved ? 'Saved in Feastbook' : 'Save to Feastbook'}
                  >
                    <Heart className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
                  </button>
                </div>

                {/* Specific Rationale banner */}
                <div className="bg-slate-800/80 px-3 py-2 rounded-xl border border-slate-700/60 text-[11px] text-slate-300 font-medium leading-relaxed">
                  <span className="text-emerald-400 font-extrabold mr-1">Why:</span>
                  {item.rationale}
                </div>

                {/* Recipe Title & Description */}
                <div>
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    {recipe.cuisine} • {recipe.difficulty}
                  </div>
                  <h3 className="text-lg font-black text-white mt-1 leading-snug group-hover:text-emerald-400 transition-colors">
                    {recipe.title}
                  </h3>
                  <p className="text-slate-300 text-xs mt-2 line-clamp-3 leading-relaxed">
                    {recipe.short_description}
                  </p>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-200 bg-slate-800/80 p-2 rounded-xl font-bold">
                    <Clock className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{recipe.cooking_time_minutes} mins</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-200 bg-slate-800/80 p-2 rounded-xl font-bold">
                    <Utensils className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{recipe.servings} Servings</span>
                  </div>
                </div>

                {/* Nutrition Snapshot */}
                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
                  <span>🔥 {recipe.nutrition_estimate.calories} kcal</span>
                  <span>💪 {recipe.nutrition_estimate.protein_g}g Protein</span>
                  <span className="text-emerald-400 font-bold">♻️ {recipe.ingredient_utilization_percentage}% Util</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 mt-3 border-t border-slate-800 space-y-2">
                <button
                  onClick={() => onSelectRecipe(recipe)}
                  className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md flex items-center justify-center gap-1.5 transition-all"
                >
                  <ChefHat className="w-4 h-4" />
                  <span>Cook This Recipe</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
