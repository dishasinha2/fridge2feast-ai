import React, { useState } from 'react';
import { Utensils, Clock, Flame, Users, Sparkles, ChefHat, RefreshCw } from 'lucide-react';
import {
  UserPreferences,
  DietPreference,
  CuisinePreference,
  CookingTimePreference,
  DifficultyPreference,
  SpiceLevelPreference,
} from '../types';

interface PreferencesFormProps {
  initialPreferences: UserPreferences;
  onGenerateRecipes: (preferences: UserPreferences) => Promise<void>;
  isGenerating: boolean;
  confirmedIngredientsCount: number;
}

const DIET_OPTIONS: DietPreference[] = ['Vegetarian', 'Vegan', 'Non-Vegetarian', 'Eggetarian', 'No Preference'];
const CUISINE_OPTIONS: CuisinePreference[] = ['Indian', 'Italian', 'Mexican', 'Asian', 'Mediterranean', 'American', 'Fusion', 'Any'];
const TIME_OPTIONS: CookingTimePreference[] = ['Under 15 minutes', 'Under 30 minutes', 'Under 60 minutes', 'No limit'];
const DIFFICULTY_OPTIONS: DifficultyPreference[] = ['Easy', 'Medium', 'Advanced'];
const SPICE_OPTIONS: SpiceLevelPreference[] = ['Mild', 'Medium', 'Spicy'];
const DIETARY_RESTRICTIONS = ['Gluten Free', 'Dairy Free', 'Nut Free', 'Low Sugar', 'High Protein'];

export const PreferencesForm: React.FC<PreferencesFormProps> = ({
  initialPreferences,
  onGenerateRecipes,
  isGenerating,
  confirmedIngredientsCount,
}) => {
  const [preferences, setPreferences] = useState<UserPreferences>(initialPreferences);

  const handleDietaryRestrictionToggle = (restriction: string) => {
    let updated: string[];
    if (preferences.dietaryRestrictions.includes(restriction)) {
      updated = preferences.dietaryRestrictions.filter((r) => r !== restriction);
    } else {
      updated = [...preferences.dietaryRestrictions, restriction];
    }
    setPreferences({ ...preferences, dietaryRestrictions: updated });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerateRecipes(preferences);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      <div className="text-center space-y-2">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-extrabold rounded-full">
          <ChefHat className="w-3.5 h-3.5 text-emerald-400" />
          Culinary Preferences
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          Personalize Your Recipe Options
        </h1>
        <p className="text-slate-300 text-sm max-w-xl mx-auto">
          Tailor recipe formulations based on diet, budget, cooking time, and spice preference.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-10 shadow-xl space-y-8">
        {/* 1. DIET SELECTION */}
        <div className="space-y-3">
          <label className="flex items-center gap-2 text-sm font-extrabold text-white">
            <Utensils className="w-4 h-4 text-emerald-400" />
            <span>Dietary Preference</span>
          </label>
          <div className="flex flex-wrap gap-2.5">
            {DIET_OPTIONS.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setPreferences({ ...preferences, diet: option })}
                className={`px-4 py-2.5 rounded-xl text-xs font-extrabold transition-all ${
                  preferences.diet === option
                    ? 'bg-emerald-600 text-white shadow-md'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>

        {/* 2. CUISINE SELECTION */}
        <div className="space-y-3">
          <label className="flex items-center gap-2 text-sm font-extrabold text-white">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>Cuisine Style</span>
          </label>
          <div className="flex flex-wrap gap-2.5">
            {CUISINE_OPTIONS.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setPreferences({ ...preferences, cuisine: option })}
                className={`px-4 py-2.5 rounded-xl text-xs font-extrabold transition-all ${
                  preferences.cuisine === option
                    ? 'bg-emerald-600 text-white shadow-md'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>

        {/* 3. TIME, DIFFICULTY, SERVINGS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2 border-t border-slate-800">
          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm font-extrabold text-white">
              <Clock className="w-4 h-4 text-emerald-400" />
              <span>Max Time</span>
            </label>
            <select
              value={preferences.cookingTime}
              onChange={(e) => setPreferences({ ...preferences, cookingTime: e.target.value as CookingTimePreference })}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs font-bold text-white outline-none focus:border-emerald-500"
            >
              {TIME_OPTIONS.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm font-extrabold text-white">
              <Flame className="w-4 h-4 text-emerald-400" />
              <span>Difficulty</span>
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {DIFFICULTY_OPTIONS.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setPreferences({ ...preferences, difficulty: d })}
                  className={`py-2 rounded-xl text-xs font-bold transition-all ${
                    preferences.difficulty === d
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm font-extrabold text-white">
              <Users className="w-4 h-4 text-emerald-400" />
              <span>Servings ({preferences.servings})</span>
            </label>
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setPreferences({ ...preferences, servings: Math.max(1, preferences.servings - 1) })}
                className="w-10 h-10 rounded-xl bg-slate-800 hover:bg-slate-700 font-bold text-lg text-white flex items-center justify-center"
              >
                -
              </button>
              <span className="font-extrabold text-white text-base w-8 text-center">{preferences.servings}</span>
              <button
                type="button"
                onClick={() => setPreferences({ ...preferences, servings: Math.min(8, preferences.servings + 1) })}
                className="w-10 h-10 rounded-xl bg-slate-800 hover:bg-slate-700 font-bold text-lg text-white flex items-center justify-center"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* 4. BUDGET IN INR & SPICE LEVEL */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4 border-t border-slate-800">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm font-extrabold text-white">
                <span>Max Missing Items Budget</span>
              </label>
              <span className="font-black text-emerald-400 bg-emerald-950 px-2.5 py-1 rounded-lg text-xs border border-emerald-500/30">
                ₹{preferences.budgetINR} {preferences.budgetINR === 0 ? '(Pantry Only)' : ''}
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="2000"
              step="25"
              value={preferences.budgetINR}
              onChange={(e) => setPreferences({ ...preferences, budgetINR: Number(e.target.value) })}
              className="w-full accent-emerald-500 cursor-pointer"
            />
          </div>

          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm font-extrabold text-white">
              <span>Spice Level</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {SPICE_OPTIONS.map((spice) => (
                <button
                  key={spice}
                  type="button"
                  onClick={() => setPreferences({ ...preferences, spiceLevel: spice })}
                  className={`py-2 rounded-xl text-xs font-bold transition-all ${
                    preferences.spiceLevel === spice
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  }`}
                >
                  {spice}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* SUBMIT BUTTON */}
        <div className="pt-6 border-t border-slate-800 text-center">
          <button
            type="submit"
            disabled={isGenerating || confirmedIngredientsCount === 0}
            id="generate-recipes-btn"
            className={`w-full py-4 rounded-2xl font-black text-base flex items-center justify-center gap-3 shadow-xl transition-all ${
              isGenerating || confirmedIngredientsCount === 0
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-950/50 hover:scale-[1.01]'
            }`}
          >
            {isGenerating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin text-white" />
                <span>Formulating 3 Zero-Waste Recipes...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>✨ Generate 3 Personalized Recipes</span>
              </>
            )}
          </button>

          {confirmedIngredientsCount === 0 && (
            <p className="text-rose-400 text-xs font-bold mt-2">
              Please select at least 1 confirmed ingredient in My Inventory first.
            </p>
          )}
        </div>
      </form>
    </div>
  );
};
