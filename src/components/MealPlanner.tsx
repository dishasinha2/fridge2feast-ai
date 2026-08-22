import React, { useState } from 'react';
import { Calendar, Clock, Utensils, ArrowRight, Leaf, Sparkles } from 'lucide-react';
import { Recipe, DetectedIngredient } from '../types';

interface MealPlannerProps {
  ingredients?: DetectedIngredient[];
  inventory?: DetectedIngredient[];
  savedRecipes: Recipe[];
  onSelectRecipe?: (recipe: Recipe) => void;
  onOpenRecipe?: (recipe: Recipe) => void;
  onGoToScan?: () => void;
  onGoToKitchenAgent: () => void;
}

type TimelineView = 'today' | '3days' | '7days';

export const MealPlanner: React.FC<MealPlannerProps> = ({
  ingredients,
  inventory,
  savedRecipes = [],
  onSelectRecipe,
  onOpenRecipe,
  onGoToScan,
  onGoToKitchenAgent,
}) => {
  const [timeline, setTimeline] = useState<TimelineView>('3days');

  const rawIngredients = inventory || ingredients || [];
  const activeIngredients = rawIngredients.filter((i) => i && i.included);

  const handleOpen = (recipe?: Recipe) => {
    if (recipe) {
      if (onSelectRecipe) onSelectRecipe(recipe);
      else if (onOpenRecipe) onOpenRecipe(recipe);
    } else {
      onGoToKitchenAgent();
    }
  };

  // If user has no saved recipes and no scanned ingredients, show clean real empty state
  if (savedRecipes.length === 0 && activeIngredients.length === 0) {
    return (
      <div className="max-w-md mx-auto my-16 bg-slate-900 rounded-2xl border border-slate-800 p-8 text-center space-y-4 shadow-xl">
        <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto font-bold">
          <Calendar className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">No Planned Meals Yet</h2>
        <p className="text-slate-400 text-xs leading-relaxed">
          Scan your fridge or save zero-waste recipes to build your personalized weekly kitchen schedule.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          {onGoToScan && (
            <button
              onClick={onGoToScan}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors"
            >
              Scan fridge
            </button>
          )}
          <button
            onClick={onGoToKitchenAgent}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs rounded-xl border border-slate-700 transition-colors"
          >
            Kitchen Agent
          </button>
        </div>
      </div>
    );
  }

  // Build actual meal slots from saved recipes and available inventory
  const mealSlots: Array<{
    id: string;
    day: string;
    date: string;
    type: string;
    time: string;
    servings: number;
    recipeName: string;
    rescuedItems: string;
    recipe?: Recipe;
  }> = [];

  const days = ['Today', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
  const types = ['Lunch', 'Dinner', 'Breakfast', 'Dinner'];

  let recipeIdx = 0;
  let ingIdx = 0;

  days.forEach((day, dayIndex) => {
    const mealType = types[dayIndex % types.length];
    const assignedRecipe = savedRecipes[recipeIdx % Math.max(1, savedRecipes.length)];
    const assignedIng = activeIngredients[ingIdx % Math.max(1, activeIngredients.length)];

    if (savedRecipes.length > 0 && assignedRecipe) {
      mealSlots.push({
        id: `slot-${dayIndex}`,
        day,
        date: day === 'Today' ? 'Tonight' : day,
        type: mealType,
        time: `${assignedRecipe.cooking_time_minutes || 25} mins`,
        servings: assignedRecipe.servings || 2,
        recipeName: assignedRecipe.title,
        rescuedItems: assignedRecipe.ingredients_available?.map((i) => i.name).slice(0, 3).join(', ') || 'Available inventory',
        recipe: assignedRecipe,
      });
      recipeIdx++;
    } else if (assignedIng) {
      mealSlots.push({
        id: `slot-${dayIndex}`,
        day,
        date: day === 'Today' ? 'Tonight' : day,
        type: mealType,
        time: '20 mins',
        servings: 2,
        recipeName: `Sautéed ${assignedIng.name} & Seasoned Pantry Feast`,
        rescuedItems: assignedIng.name,
      });
      ingIdx++;
    }
  });

  const visibleSlots = timeline === 'today'
    ? mealSlots.filter((m) => m.day === 'Today')
    : timeline === '3days'
    ? mealSlots.slice(0, 3)
    : mealSlots.slice(0, 7);

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
            <Calendar className="w-3.5 h-3.5" />
            <span>Kitchen Calendar</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Meal Planner
          </h1>
          <p className="text-slate-400 text-sm">
            Practical meals scheduled chronologically using your available ingredients.
          </p>
        </div>

        {/* View Switcher: Today | 3 Days | 7 Days */}
        <div className="inline-flex p-1 bg-slate-900 border border-slate-800 rounded-xl self-start sm:self-auto text-xs font-semibold">
          <button
            onClick={() => setTimeline('today')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              timeline === 'today' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Today
          </button>
          <button
            onClick={() => setTimeline('3days')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              timeline === '3days' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            3 Days
          </button>
          <button
            onClick={() => setTimeline('7days')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              timeline === '7days' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            7 Days
          </button>
        </div>
      </div>

      {/* CHRONOLOGICAL MEAL FEED */}
      <div className="space-y-4">
        {visibleSlots.map((slot) => (
          <div
            key={slot.id}
            className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-xs">
                <span className="font-bold text-emerald-400 uppercase tracking-wide">
                  {slot.day} · {slot.type}
                </span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {slot.time}
                </span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-400 flex items-center gap-1">
                  <Utensils className="w-3 h-3 text-slate-400" />
                  {slot.servings} servings
                </span>
              </div>

              <h3 className="text-base font-bold text-white leading-tight">
                {slot.recipeName}
              </h3>

              <div className="text-xs text-slate-400 flex items-center gap-1.5">
                <Leaf className="w-3.5 h-3.5 text-emerald-400" />
                <span>Rescues: <strong className="text-slate-300 font-medium">{slot.rescuedItems}</strong></span>
              </div>
            </div>

            <div className="flex items-center gap-2 self-start sm:self-auto">
              <button
                onClick={() => handleOpen(slot.recipe)}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
              >
                Cook meal
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
