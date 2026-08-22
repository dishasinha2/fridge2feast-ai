import React, { useState, useEffect } from 'react';
import { Clock, Utensils, Leaf, DollarSign, ArrowLeft, Heart, Download, CheckCircle2, Circle, ChefHat, Sparkles } from 'lucide-react';
import confetti from 'canvas-confetti';
import { Recipe, UserPreferences } from '../types';
import { WasteScoreBadge } from './WasteScoreBadge';
import { SmartShoppingList } from './SmartShoppingList';
import { RecipeAiAssistant } from './RecipeAiAssistant';
import { exportRecipeAsMarkdown } from '../utils/export';

interface RecipeDashboardProps {
  recipe: Recipe;
  preferences: UserPreferences;
  totalConfirmedIngredientsCount: number;
  onBackToResults: () => void;
  onSaveFavorite: (recipe: Recipe) => void;
  isSaved: boolean;
}

export const RecipeDashboard: React.FC<RecipeDashboardProps> = ({
  recipe,
  preferences,
  totalConfirmedIngredientsCount,
  onBackToResults,
  onSaveFavorite,
  isSaved,
}) => {
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});
  const [activeStepIndex, setActiveStepIndex] = useState<number>(0);

  useEffect(() => {
    try {
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.6 },
      });
    } catch (e) {
      // Ignore if web environment blocks canvas
    }
  }, [recipe.id]);

  const toggleStep = (index: number) => {
    setCompletedSteps((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const availableCount = recipe.ingredients_available.length;
  const totalSteps = recipe.preparation_steps.length;

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-4">
      {/* Top Back & Action Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBackToResults}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-bold text-xs flex items-center gap-2 transition-colors border border-slate-700"
          id="back-to-results-btn"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Menu Results</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onSaveFavorite(recipe)}
            className={`px-4 py-2 rounded-xl text-xs font-extrabold flex items-center gap-2 border transition-all ${
              isSaved
                ? 'bg-rose-950/80 text-rose-300 border-rose-800'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <Heart className={`w-4 h-4 ${isSaved ? 'fill-current text-rose-400' : ''}`} />
            <span>{isSaved ? 'Saved in Feastbook' : 'Save to Feastbook'}</span>
          </button>

          <button
            onClick={() => exportRecipeAsMarkdown(recipe)}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-extrabold flex items-center gap-2 shadow-md transition-colors"
          >
            <Download className="w-4 h-4 text-white" />
            <span>Export Markdown</span>
          </button>
        </div>
      </div>

      {/* RECIPE TITLE BANNER */}
      <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-10 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-black px-3 py-1 rounded-full bg-emerald-600 text-white uppercase tracking-wider">
            {recipe.badge}
          </span>
          <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {recipe.cuisine} Cuisine
          </span>
          <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {recipe.difficulty} Level
          </span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
          🍳 {recipe.title}
        </h1>

        <p className="text-slate-300 text-sm leading-relaxed max-w-3xl">
          {recipe.short_description}
        </p>

        {/* TOP KPI METRIC CARDS */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-800">
          <div className="bg-slate-800/80 p-4 rounded-2xl border border-slate-700 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-emerald-400" />
              Cooking Time
            </span>
            <p className="text-xl font-black text-white">{recipe.cooking_time_minutes} mins</p>
          </div>

          <div className="bg-slate-800/80 p-4 rounded-2xl border border-slate-700 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1">
              <Utensils className="w-3.5 h-3.5 text-emerald-400" />
              Servings
            </span>
            <p className="text-xl font-black text-white">{recipe.servings} Servings</p>
          </div>

          <div className="bg-emerald-950/60 p-4 rounded-2xl border border-emerald-500/30 space-y-1">
            <span className="text-[11px] font-bold text-emerald-400 uppercase flex items-center gap-1">
              <Leaf className="w-3.5 h-3.5 text-emerald-400" />
              Utilization
            </span>
            <p className="text-xl font-black text-emerald-400">{recipe.ingredient_utilization_percentage}%</p>
          </div>

          <div className="bg-slate-800/80 p-4 rounded-2xl border border-slate-700 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
              Extra Cost
            </span>
            <p className="text-xl font-black text-white">
              {recipe.estimated_missing_cost_inr === 0 ? '₹0' : `₹${recipe.estimated_missing_cost_inr}`}
            </p>
          </div>
        </div>
      </div>

      {/* FOOD WASTE SCORE COMPONENT */}
      <WasteScoreBadge
        usedAvailableCount={availableCount}
        totalAvailableCount={totalConfirmedIngredientsCount || availableCount}
        recipeUtilizationPercentage={recipe.ingredient_utilization_percentage}
      />

      {/* INGREDIENTS LIST: AVAILABLE VS MISSING */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <h3 className="font-extrabold text-white text-lg">
              Ingredients From Your Fridge ({recipe.ingredients_available.length})
            </h3>
          </div>

          <ul className="space-y-2.5 text-sm">
            {recipe.ingredients_available.map((ing, idx) => (
              <li key={idx} className="flex items-center justify-between p-2.5 bg-slate-800/60 rounded-xl border border-slate-700">
                <span className="font-extrabold text-white">{ing.name}</span>
                <span className="text-xs font-bold text-emerald-400">{ing.quantity}</span>
              </li>
            ))}
          </ul>
        </div>

        <SmartShoppingList missingIngredients={recipe.ingredients_missing} recipeTitle={recipe.title} />
      </div>

      {/* 18. COOKING MODE / STEP-BY-STEP */}
      <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="space-y-1">
            <h3 className="text-xl font-black text-white flex items-center gap-2">
              <ChefHat className="w-5 h-5 text-emerald-400" />
              <span>👨‍🍳 Cooking Mode</span>
            </h3>
            <p className="text-slate-400 text-xs">Step {activeStepIndex + 1} of {totalSteps}</p>
          </div>

          {/* Progress Bar */}
          <div className="w-36 bg-slate-800 rounded-full h-2.5 overflow-hidden border border-slate-700">
            <div
              className="bg-emerald-500 h-full transition-all duration-300"
              style={{ width: `${((activeStepIndex + 1) / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Active Cooking Step Card */}
        <div className="p-6 bg-slate-950 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-black text-emerald-400 uppercase tracking-widest">
              Step {activeStepIndex + 1}
            </span>
            <button
              onClick={() => toggleStep(activeStepIndex)}
              className={`px-3 py-1 rounded-xl text-xs font-bold border transition-colors ${
                completedSteps[activeStepIndex]
                  ? 'bg-emerald-950 text-emerald-400 border-emerald-500/40'
                  : 'bg-slate-800 text-slate-300 border-slate-700'
              }`}
            >
              {completedSteps[activeStepIndex] ? '✓ Step Completed' : 'Mark Complete'}
            </button>
          </div>

          <p className="text-base font-extrabold text-white leading-relaxed">
            {recipe.preparation_steps[activeStepIndex]}
          </p>

          {/* Chef Tip for Step if available */}
          {recipe.cooking_tips[activeStepIndex % recipe.cooking_tips.length] && (
            <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 flex items-start gap-2 text-xs text-amber-300">
              <Sparkles className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <span>Chef Tip: {recipe.cooking_tips[activeStepIndex % recipe.cooking_tips.length]}</span>
            </div>
          )}
        </div>

        {/* Navigation Controls */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setActiveStepIndex((prev) => Math.max(0, prev - 1))}
            disabled={activeStepIndex === 0}
            className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-white font-extrabold text-xs rounded-xl border border-slate-700 transition-colors"
          >
            ← Previous Step
          </button>

          <button
            onClick={() => {
              toggleStep(activeStepIndex);
              if (activeStepIndex < totalSteps - 1) {
                setActiveStepIndex(activeStepIndex + 1);
              }
            }}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md transition-all"
          >
            {activeStepIndex === totalSteps - 1 ? '✓ Complete Recipe' : '✓ Complete & Next Step →'}
          </button>
        </div>
      </div>

      {/* NUTRITION & TIPS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-black text-white">Nutrition Estimate (Per Serving)</h3>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-slate-800/80 rounded-xl text-center border border-slate-700">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Calories</span>
              <p className="text-lg font-black text-white">{recipe.nutrition_estimate.calories} kcal</p>
            </div>
            <div className="p-3 bg-slate-800/80 rounded-xl text-center border border-slate-700">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Protein</span>
              <p className="text-lg font-black text-white">{recipe.nutrition_estimate.protein_g}g</p>
            </div>
            <div className="p-3 bg-slate-800/80 rounded-xl text-center border border-slate-700">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Carbs</span>
              <p className="text-lg font-black text-white">{recipe.nutrition_estimate.carbs_g}g</p>
            </div>
            <div className="p-3 bg-slate-800/80 rounded-xl text-center border border-slate-700">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Fat</span>
              <p className="text-lg font-black text-white">{recipe.nutrition_estimate.fat_g}g</p>
            </div>
            <div className="p-3 bg-slate-800/80 rounded-xl text-center border border-slate-700">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Fiber</span>
              <p className="text-lg font-black text-white">{recipe.nutrition_estimate.fiber_g}g</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-black text-white">Smart Substitutions & Chef Tips</h3>

          <div className="space-y-3 text-xs">
            {recipe.substitutions.map((sub, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-300">
                <span className="font-extrabold">Swap {sub.original} → {sub.substitute}: </span>
                <span>{sub.note}</span>
              </div>
            ))}

            {recipe.cooking_tips.map((tip, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-800/80 border border-slate-700 flex items-start gap-2 text-slate-200">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span className="font-medium">{tip}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CONTEXTUAL AI SOUS-CHEF ASSISTANT */}
      <RecipeAiAssistant recipe={recipe} preferences={preferences} />
    </div>
  );
};
