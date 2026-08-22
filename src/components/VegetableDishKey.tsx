import React from 'react';
import { Sparkles, Utensils, CheckCircle2, ArrowRight, ChefHat, Flame, Clock } from 'lucide-react';
import { DetectedIngredient } from '../types';

interface VegetableDishKeyProps {
  ingredients: DetectedIngredient[];
  onGenerateRecipesWithKey?: (vegetableNames?: string[]) => void;
  onOpenRecipeStudio?: () => void;
}

interface VegetableCombinationRule {
  id: string;
  name: string;
  requiredVeggies: string[];
  dishName: string;
  category: string;
  timeEstimate: string;
  difficulty: 'Easy' | 'Medium';
  description: string;
  tags: string[];
}

const COMMON_CULINARY_RULES: VegetableCombinationRule[] = [
  {
    id: 'combo-shakshuka',
    name: 'Tomatoes + Peppers + Onions',
    requiredVeggies: ['tomato', 'pepper', 'capsicum', 'onion'],
    dishName: 'Spiced Shakshuka Skillet / Paneer Bhurji',
    category: 'Skillet & Stews',
    timeEstimate: '18 mins',
    difficulty: 'Easy',
    description: 'Simmer sweet bell peppers and tangy tomatoes into a rich savory base topped with soft eggs or paneer.',
    tags: ['Zero-Waste', 'High Protein', 'Comfort Food'],
  },
  {
    id: 'combo-stirfry',
    name: 'Broccoli + Carrots + Garlic',
    requiredVeggies: ['broccoli', 'carrot', 'garlic'],
    dishName: 'Crispy Garlic Asian Veggie Stir-Fry',
    category: 'Wok & Bowls',
    timeEstimate: '12 mins',
    difficulty: 'Easy',
    description: 'High-heat wok-seared crunchy florets and carrots tossed in aromatic garlic, soy glaze, and sesame.',
    tags: ['Super Fast', 'High Fiber', 'Crunchy'],
  },
  {
    id: 'combo-palak',
    name: 'Spinach + Garlic + Paneer/Cheese',
    requiredVeggies: ['spinach', 'palak', 'paneer', 'cheese', 'garlic'],
    dishName: 'Palak Paneer Skillet / Spinach Frittata',
    category: 'Curries & Bakes',
    timeEstimate: '22 mins',
    difficulty: 'Medium',
    description: 'Velvety puréed or sautéed greens infused with garlic and tossed with golden seared cottage cheese.',
    tags: ['Iron Rich', 'Nutrient Dense', 'Homestyle'],
  },
  {
    id: 'combo-pasta',
    name: 'Tomatoes + Garlic + Herbs/Cheese',
    requiredVeggies: ['tomato', 'garlic', 'cheese', 'basil'],
    dishName: 'Rustic Fresh Garden Pomodoro Pasta',
    category: 'Italian & Pastas',
    timeEstimate: '15 mins',
    difficulty: 'Easy',
    description: 'Sweet burst tomatoes melted with fragrant garlic olive oil over tender pasta or roasted sourdough.',
    tags: ['Pantry Classic', 'Family Favorite', 'Vegetarian'],
  },
  {
    id: 'combo-curry',
    name: 'Potatoes + Peas + Onions',
    requiredVeggies: ['potato', 'pea', 'onion', 'ginger'],
    dishName: 'Homestyle Aloo Matar & Spiced Toasties',
    category: 'Curries & Street Food',
    timeEstimate: '20 mins',
    difficulty: 'Easy',
    description: 'Tender potatoes and sweet green peas simmered in mild cumin-coriander gravy or stuffed into grilled sandwiches.',
    tags: ['Crowd Pleaser', 'Hearty', 'Affordable'],
  },
  {
    id: 'combo-mushroom',
    name: 'Mushrooms + Onions + Herbs',
    requiredVeggies: ['mushroom', 'onion', 'butter', 'pepper'],
    dishName: 'Caramelized Garlic Herb Butter Mushrooms',
    category: 'Appetizers & Toasts',
    timeEstimate: '10 mins',
    difficulty: 'Easy',
    description: 'Golden-seared earthy mushrooms basted in savory garlic butter over crispy toast or steamed rice.',
    tags: ['Gourmet', 'Ultra Fast', 'Rich Umami'],
  },
];

export const VegetableDishKey: React.FC<VegetableDishKeyProps> = ({
  ingredients = [],
  onGenerateRecipesWithKey = (_v?: string[]) => {},
  onOpenRecipeStudio = () => {},
}) => {
  const activeIngredients = ingredients.filter((i) => i.included);
  const ingredientNames = activeIngredients.map((i) => i.name.toLowerCase());

  // Match which combos the user currently has ingredients for
  const matchedCombos = COMMON_CULINARY_RULES.map((rule) => {
    const matchingCount = rule.requiredVeggies.filter((rv) =>
      ingredientNames.some((name) => name.includes(rv))
    ).length;

    const matchScore = rule.requiredVeggies.length > 0
      ? Math.min(100, Math.round((matchingCount / Math.min(2, rule.requiredVeggies.length)) * 100))
      : 0;

    const availableMatchedVeggies = activeIngredients.filter((ing) =>
      rule.requiredVeggies.some((rv) => ing.name.toLowerCase().includes(rv))
    );

    return {
      ...rule,
      matchScore,
      isUnlocked: matchingCount >= 2 || (matchingCount >= 1 && activeIngredients.length <= 2),
      matchingCount,
      availableMatchedVeggies,
    };
  }).sort((a, b) => b.matchScore - a.matchScore);

  const hasAnyUnlocked = matchedCombos.some((c) => c.isUnlocked);
  const totalVegCount = activeIngredients.filter((i) => i.category === 'Vegetable' || i.category === 'Fruit').length;

  return (
    <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl relative overflow-hidden">
      {/* Background Accent Glow */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-extrabold border border-emerald-500/30">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>VEGETABLE-TO-FEAST KEY</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            🔑 What You Can Make From Your Vegetables
          </h2>
          <p className="text-slate-400 text-xs sm:text-sm max-w-2xl">
            Here is your exact culinary key: which scanned vegetables unlock which delicious, edible meals.
          </p>
        </div>

        {totalVegCount > 0 && (
          <div className="bg-slate-800/80 px-4 py-2 rounded-2xl border border-slate-700 text-right flex-shrink-0">
            <span className="text-[11px] font-bold text-slate-400 uppercase block">Active Vegetables</span>
            <span className="text-lg font-black text-emerald-400">🥕 {totalVegCount} Items Ready</span>
          </div>
        )}
      </div>

      {/* MATCHED COMBINATIONS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {matchedCombos.slice(0, 6).map((combo) => {
          const isHighMatch = combo.matchScore >= 70;

          return (
            <div
              key={combo.id}
              className={`rounded-2xl p-5 border flex flex-col justify-between transition-all duration-200 relative ${
                combo.isUnlocked
                  ? 'bg-slate-800/90 border-emerald-500/40 shadow-lg shadow-emerald-950/20'
                  : 'bg-slate-900/60 border-slate-800 opacity-80 hover:opacity-100'
              }`}
            >
              <div className="space-y-3">
                {/* Header Tag & Status */}
                <div className="flex items-center justify-between">
                  <span className={`text-[11px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                    combo.isUnlocked
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {combo.isUnlocked ? '✨ Unlocked Feast' : '💡 Kitchen Idea'}
                  </span>

                  <span className="text-xs font-bold text-slate-400 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-emerald-400" />
                    {combo.timeEstimate}
                  </span>
                </div>

                {/* Dish Name */}
                <div>
                  <h3 className="font-black text-white text-base leading-snug">
                    {combo.dishName}
                  </h3>
                  <p className="text-slate-300 text-xs mt-1.5 leading-relaxed">
                    {combo.description}
                  </p>
                </div>

                {/* Key Vegetables Formula */}
                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80 space-y-1">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block">
                    🔑 Key Ingredients:
                  </span>
                  <p className="text-xs font-bold text-emerald-300">
                    {combo.name}
                  </p>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {combo.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] font-bold px-2 py-0.5 bg-slate-800 text-slate-300 rounded-md border border-slate-700"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <div className="pt-4 mt-3 border-t border-slate-800/80">
                <button
                  onClick={() => {
                    const matchedNames = combo.availableMatchedVeggies.map((v) => v.name);
                    if (matchedNames.length > 0) {
                      onGenerateRecipesWithKey(matchedNames);
                    } else {
                      onOpenRecipeStudio();
                    }
                  }}
                  className={`w-full py-2 px-3 rounded-xl text-xs font-extrabold flex items-center justify-center gap-1.5 transition-all ${
                    combo.isUnlocked
                      ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                  }`}
                >
                  <ChefHat className="w-3.5 h-3.5" />
                  <span>{combo.isUnlocked ? 'Formulate This Feast' : 'Cook With This Idea'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
