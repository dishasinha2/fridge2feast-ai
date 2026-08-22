import React, { useState } from 'react';
import { AlertCircle, Clock, ShieldAlert, Sparkles, ArrowRight, Check, Calendar } from 'lucide-react';
import { DetectedIngredient, Recipe } from '../types';

interface RescueModeProps {
  ingredients?: DetectedIngredient[];
  onSelectRecipe?: (recipe: Recipe) => void;
  onGoToScanner?: () => void;
  onGoToScan?: () => void;
  onFindRescueMeal?: () => void;
  onGenerateRescueRecipes?: (preferences: any) => Promise<void>;
  isGenerating?: boolean;
  onUpdateIngredients?: (ingredients: DetectedIngredient[]) => void;
}

export const RescueMode: React.FC<RescueModeProps> = ({
  ingredients = [],
  onSelectRecipe,
  onGoToScanner,
  onGoToScan,
  onFindRescueMeal,
  onGenerateRescueRecipes,
  isGenerating = false,
}) => {
  const [showPlan, setShowPlan] = useState<boolean>(false);

  const activeIngredients = ingredients.filter((i) => i && i.included);
  
  // Categorize by perishability risk
  const highPriorityItems = activeIngredients.filter(
    (i) => i.category === 'Vegetable' || i.category === 'Dairy' || i.category === 'Meat/Seafood' || i.category === 'Fruit'
  ).slice(0, 4);

  const estSavingsINR = highPriorityItems.length * 60;

  const handleTriggerRescue = () => {
    if (onGenerateRescueRecipes) {
      onGenerateRescueRecipes({
        diet: 'No Preference',
        cookingTime: 'Under 30 minutes',
        difficulty: 'Easy',
        servings: 2,
        spiceLevel: 'Medium',
      });
    } else if (onFindRescueMeal) {
      onFindRescueMeal();
    }
  };

  const handleGoToScan = onGoToScan || onGoToScanner || (() => {});

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 space-y-8">
      {/* Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 text-xs font-semibold">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Waste Prevention</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Rescue your fridge
        </h1>
        <p className="text-slate-400 text-sm sm:text-base">
          Let's use the ingredients that need attention first.
        </p>
      </div>

      {activeIngredients.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center space-y-4">
          <p className="text-slate-300 text-sm">
            Your inventory is currently empty. Scan your fridge or add ingredients to see items that need attention.
          </p>
          <button
            onClick={handleGoToScan}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl transition-colors"
          >
            Scan my fridge
          </button>
        </div>
      ) : (
        <>
          {/* Summary Banner */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-0.5">
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                Potential Impact
              </span>
              <div className="text-base font-bold text-white">
                {highPriorityItems.length} perishable items ready for cooking (~₹{estSavingsINR} value protected)
              </div>
            </div>
            <button
              onClick={() => {
                setShowPlan(true);
                handleTriggerRescue();
              }}
              disabled={isGenerating}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-md transition-all whitespace-nowrap self-start sm:self-auto flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Crafting rescue meals...</span>
                </>
              ) : (
                <span>Build my rescue plan</span>
              )}
            </button>
          </div>

          {/* HIGH PRIORITY LIST */}
          <section className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              High Priority Items
            </h2>
            <div className="space-y-2.5">
              {highPriorityItems.length > 0 ? (
                highPriorityItems.map((item, idx) => (
                  <div
                    key={item.id || idx}
                    className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-slate-700 transition-colors"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-sm">{item.name}</span>
                        <span className="text-xs text-slate-400">({item.estimated_quantity})</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          HIGH PRIORITY
                        </span>
                      </div>
                      <p className="text-xs text-slate-400">
                        Best used in your next meal to preserve flavor, vitamins and avoid spoilage.
                      </p>
                    </div>

                    <button
                      onClick={handleTriggerRescue}
                      disabled={isGenerating}
                      className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors self-start sm:self-auto flex items-center gap-1"
                    >
                      <span>Cook with {item.name.toLowerCase()}</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                ))
              ) : (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center text-xs text-slate-400">
                  No high-risk items detected right now. Everything in your pantry looks stable!
                </div>
              )}
            </div>
          </section>

          {/* 3-DAY PRACTICAL RESCUE SCHEDULE */}
          <section className="space-y-4 pt-2">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-emerald-400" />
              <span>3-Day Rescue Plan</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Tonight */}
              <div className="bg-slate-900 border border-emerald-500/30 rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-400 uppercase">Tonight</span>
                  <span className="text-[11px] text-slate-400">Urgent items</span>
                </div>
                <div className="space-y-1">
                  <div className="font-bold text-white text-sm">
                    {highPriorityItems[0] ? `Fresh ${highPriorityItems[0].name} Stir-Fry` : 'Pantry Sauté'}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Uses tender greens & aromatics immediately at peak moisture.
                  </p>
                </div>
                <div className="text-[11px] text-emerald-400/90 font-medium">
                  Rescues: {highPriorityItems.slice(0, 2).map((i) => i.name).join(', ') || 'Fresh vegetables'}
                </div>
              </div>

              {/* Tomorrow */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-300 uppercase">Tomorrow</span>
                  <span className="text-[11px] text-slate-400">Mid perishable</span>
                </div>
                <div className="space-y-1">
                  <div className="font-bold text-white text-sm">
                    {highPriorityItems[1] ? `Warm ${highPriorityItems[1].name} Bowl` : 'Hearty Grain Bowl'}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Combines hearty root vegetables with pantry legumes.
                  </p>
                </div>
                <div className="text-[11px] text-slate-300 font-medium">
                  Rescues: {highPriorityItems.slice(1, 3).map((i) => i.name).join(', ') || 'Pantry proteins'}
                </div>
              </div>

              {/* Day 3 */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-300 uppercase">Day 3</span>
                  <span className="text-[11px] text-slate-400">Stable staples</span>
                </div>
                <div className="space-y-1">
                  <div className="font-bold text-white text-sm">Pantry Fragrant Pilaf & Curry</div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Zero-waste consolidation of dry grains, spices and sturdy ingredients.
                  </p>
                </div>
                <div className="text-[11px] text-slate-300 font-medium">
                  Rescues: Remaining inventory & pantry spices
                </div>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
};
