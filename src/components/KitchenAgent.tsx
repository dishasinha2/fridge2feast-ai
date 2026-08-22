import React, { useState } from 'react';
import { Sparkles, ArrowRight, Check, RotateCcw, Flame, Clock, Users, Utensils } from 'lucide-react';
import { UserPreferences, DetectedIngredient } from '../types';

interface KitchenAgentProps {
  ingredients?: DetectedIngredient[];
  confirmedIngredientsCount?: number;
  initialPreferences: UserPreferences;
  onGenerateRecipes: (preferences: UserPreferences) => Promise<void>;
  isGenerating: boolean;
  onGoToScanner?: () => void;
  onGoToScan?: () => void;
}

const CRAVING_OPTIONS = [
  { id: 'Spicy', label: 'Spicy', icon: '🌶️', desc: 'Bold, warming & flavorful' },
  { id: 'Light', label: 'Something light', icon: '🥗', desc: 'Fresh, crisp & easy to digest' },
  { id: 'Comfort Food', label: 'Comfort food', icon: '🍲', desc: 'Warm, satisfying & hearty' },
  { id: 'Sweet', label: 'Something sweet', icon: '🍯', desc: 'Mild sweetness or dessert-inspired' },
  { id: 'Surprise Me', label: 'Surprise me', icon: '✨', desc: 'Chef’s creative recommendation' },
];

const MEAL_TIMING_OPTIONS = [
  { id: 'Breakfast', label: 'Breakfast', icon: '🌅', time: 'Under 15 mins' },
  { id: 'Lunch', label: 'Lunch', icon: '☀️', time: 'Under 30 mins' },
  { id: 'Dinner', label: 'Dinner', icon: '🌙', time: 'Under 45 mins' },
  { id: 'Evening Snack', label: 'Evening snack', icon: '☕', time: 'Under 20 mins' },
];

const HUNGER_LEVELS = [
  { id: 'Light', label: 'Light bite', desc: 'Quick snack or small meal', timePref: 'Under 15 minutes' as const },
  { id: 'Medium', label: 'Regular meal', desc: 'Standard balanced portion', timePref: 'Under 30 minutes' as const },
  { id: 'Very Hungry', label: 'Hearty & filling', desc: 'Generous feast with wholesome sides', timePref: 'Under 60 minutes' as const },
];

const HOUSEHOLD_OPTIONS = [
  { id: 1, label: 'Just me', servings: 1 },
  { id: 2, label: '2 people', servings: 2 },
  { id: 4, label: 'Family (3–4)', servings: 4 },
];

export const KitchenAgent: React.FC<KitchenAgentProps> = ({
  ingredients = [],
  initialPreferences,
  onGenerateRecipes,
  isGenerating,
  onGoToScanner,
  onGoToScan,
}) => {
  const [step, setStep] = useState<number>(1);
  const [craving, setCraving] = useState<string>('Comfort Food');
  const [mealTiming, setMealTiming] = useState<string>('Dinner');
  const [hunger, setHunger] = useState<string>('Medium');
  const [servings, setServings] = useState<number>(initialPreferences.servings || 2);
  const [diet, setDiet] = useState<string>(initialPreferences.diet || 'Vegetarian');

  const activeIngredients = ingredients.filter((i) => i.included);
  const useSoonItems = activeIngredients.filter(
    (i) => i.confidence_label === 'High' && (i.category === 'Vegetable' || i.category === 'Dairy')
  ).slice(0, 3);

  const handleFinishAndGenerate = () => {
    let spiceLevel: 'Mild' | 'Medium' | 'Spicy' = 'Medium';
    if (craving === 'Spicy') spiceLevel = 'Spicy';
    else if (craving === 'Sweet' || craving === 'Light') spiceLevel = 'Mild';

    let cookingTime: 'Under 15 minutes' | 'Under 30 minutes' | 'Under 60 minutes' | 'No limit' = 'Under 30 minutes';
    if (hunger === 'Light' || mealTiming === 'Breakfast') cookingTime = 'Under 15 minutes';
    else if (hunger === 'Very Hungry') cookingTime = 'Under 60 minutes';

    const finalPrefs: UserPreferences = {
      ...initialPreferences,
      diet: diet as any,
      servings,
      spiceLevel,
      cookingTime,
    };

    onGenerateRecipes(finalPrefs);
  };

  if (activeIngredients.length === 0) {
    return (
      <div className="max-w-xl mx-auto py-16 px-4 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto text-2xl">
          👨‍🍳
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white tracking-tight">No ingredients in your kitchen yet</h2>
          <p className="text-slate-400 text-sm leading-relaxed max-w-md mx-auto">
            Scan your fridge or add a few items first so your Kitchen Agent knows what you have to work with.
          </p>
        </div>
        <button
          onClick={onGoToScan || onGoToScanner}
          className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm rounded-xl shadow-md transition-colors inline-flex items-center gap-2"
        >
          <span>Scan my fridge</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-6 px-4 sm:px-6 space-y-8">
      {/* Header */}
      <div className="space-y-1.5">
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          What are we cooking?
        </h1>
        <p className="text-slate-400 text-sm sm:text-base">
          I've checked your kitchen ({activeIngredients.length} ingredients ready). Let's tailor the perfect meal.
        </p>
      </div>

      {/* Freshness Intelligence Notice */}
      {useSoonItems.length > 0 && (
        <div className="bg-slate-900 border border-amber-500/30 rounded-xl p-3.5 flex items-center justify-between text-xs text-slate-300">
          <div className="flex items-center gap-2">
            <span className="text-amber-400 font-semibold">Priority ingredients:</span>
            <span className="text-white font-medium">
              {useSoonItems.map((i) => i.name).join(', ')}
            </span>
          </div>
          <span className="text-amber-400/90 text-[11px]">Will be prioritized first</span>
        </div>
      )}

      {/* Progressive Step Container */}
      <div className="space-y-8">
        {/* Step 1: Craving */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              1. What are you craving?
            </h2>
            {step > 1 && (
              <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> Selected
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {CRAVING_OPTIONS.map((opt) => {
              const isSelected = craving === opt.id;
              return (
                <button
                  key={opt.id}
                  onClick={() => {
                    setCraving(opt.id);
                    if (step === 1) setStep(2);
                  }}
                  className={`p-3.5 rounded-xl border text-left transition-all ${
                    isSelected
                      ? 'bg-emerald-950/40 border-emerald-500 text-white shadow-sm'
                      : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  <div className="text-lg mb-1">{opt.icon}</div>
                  <div className="font-semibold text-sm">{opt.label}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">{opt.desc}</div>
                </button>
              );
            })}
          </div>
        </section>

        {/* Step 2: Meal Timing */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              2. When are you eating?
            </h2>
            {step > 2 && (
              <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> Selected
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {MEAL_TIMING_OPTIONS.map((opt) => {
              const isSelected = mealTiming === opt.id;
              return (
                <button
                  key={opt.id}
                  onClick={() => {
                    setMealTiming(opt.id);
                    if (step <= 2) setStep(3);
                  }}
                  className={`p-3.5 rounded-xl border text-left transition-all ${
                    isSelected
                      ? 'bg-emerald-950/40 border-emerald-500 text-white shadow-sm'
                      : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  <div className="text-lg mb-1">{opt.icon}</div>
                  <div className="font-semibold text-sm">{opt.label}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">{opt.time}</div>
                </button>
              );
            })}
          </div>
        </section>

        {/* Step 3: Hunger Level & Household */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              3. How hungry are you?
            </h2>
            <div className="space-y-2">
              {HUNGER_LEVELS.map((opt) => {
                const isSelected = hunger === opt.id;
                return (
                  <button
                    key={opt.id}
                    onClick={() => {
                      setHunger(opt.id);
                      if (step <= 3) setStep(4);
                    }}
                    className={`w-full p-3 rounded-xl border text-left flex items-center justify-between transition-all ${
                      isSelected
                        ? 'bg-emerald-950/40 border-emerald-500 text-white'
                        : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="font-medium text-sm">{opt.label}</div>
                      <div className="text-[11px] text-slate-400">{opt.desc}</div>
                    </div>
                    {isSelected && <Check className="w-4 h-4 text-emerald-400" />}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              4. Who's eating?
            </h2>
            <div className="space-y-2">
              {HOUSEHOLD_OPTIONS.map((opt) => {
                const isSelected = servings === opt.servings;
                return (
                  <button
                    key={opt.id}
                    onClick={() => {
                      setServings(opt.servings);
                      if (step <= 4) setStep(5);
                    }}
                    className={`w-full p-3 rounded-xl border text-left flex items-center justify-between transition-all ${
                      isSelected
                        ? 'bg-emerald-950/40 border-emerald-500 text-white'
                        : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="font-medium text-sm">{opt.label}</div>
                    <span className="text-xs text-slate-400 font-mono">{opt.servings} serving{opt.servings > 1 ? 's' : ''}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* Selected Preferences Summary Strip */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Selected Preference Profile
            </div>
            <div className="text-sm font-medium text-emerald-400">
              {diet} · {mealTiming} · {servings} {servings === 1 ? 'person' : 'people'} · {craving}
            </div>
          </div>

          <button
            onClick={handleFinishAndGenerate}
            disabled={isGenerating}
            className="w-full sm:w-auto px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-emerald-950/40 flex items-center justify-center gap-2 transition-transform active:scale-98 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <Sparkles className="w-4 h-4 animate-spin" />
                <span>Formulating recipes...</span>
              </>
            ) : (
              <>
                <span>Find my meal →</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
