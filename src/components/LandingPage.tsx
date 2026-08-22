import React from 'react';
import { Camera, ListCheck, ArrowRight, Sparkles, UtensilsCrossed, BookMarked, ChefHat, UserPlus } from 'lucide-react';
import { Recipe, DetectedIngredient } from '../types';
import { SAMPLE_FRIDGE_PRESETS, PresetFridge } from '../data/sampleData';
import { useAuth } from '../context/AuthContext';
import { VegetableDishKey } from './VegetableDishKey';
import { RecommendedFeasts } from './RecommendedFeasts';
import { RecommendationCardData } from '../utils/recommendations';

interface LandingPageProps {
  onStartScan: () => void;
  onGoToInventory?: () => void;
  onGoToKitchenAgent?: () => void;
  onGoToRescue?: () => void;
  onGoToRecipes?: () => void;
  onGoToFeastbook?: () => void;
  onSelectPreset: (preset: PresetFridge) => void;
  onSelectRecipe?: (recipe: Recipe) => void;
  onSaveFavorite?: (recipe: Recipe) => void;
  onLoadIngredientsFromRecipe?: (recipe: Recipe) => void;
  ingredients?: DetectedIngredient[];
  recipes?: Recipe[];
  savedRecipes?: Recipe[];
  recommendations?: RecommendationCardData[];
  isFreshUser?: boolean;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartScan,
  onGoToInventory = () => {},
  onGoToKitchenAgent = () => {},
  onGoToRescue = () => {},
  onGoToRecipes = () => {},
  onGoToFeastbook = () => {},
  onSelectPreset,
  onSelectRecipe = (_r: Recipe) => {},
  onSaveFavorite = (_r: Recipe) => {},
  onLoadIngredientsFromRecipe = (_r: Recipe) => {},
  ingredients = [],
  recipes = [],
  savedRecipes = [],
  recommendations = [],
  isFreshUser = true,
}) => {
  const { user, isGuest, setCurrentAuthView } = useAuth();

  const activeIngredients = (ingredients || []).filter((ing) => ing?.included);
  const confirmedCount = activeIngredients.length;
  const recipesCount = (recipes || []).length;
  
  // Urgent items for "Use these soon"
  const urgentItems = activeIngredients.filter(
    (i) => i.category === 'Vegetable' || i.category === 'Dairy' || i.category === 'Meat/Seafood'
  ).slice(0, 3);
  const urgentCount = urgentItems.length;

  // Time-based greeting
  const currentHour = new Date().getHours();
  let timeGreeting = 'Good evening';
  let mealPrompt = 'What should I cook tonight?';
  if (currentHour < 12) {
    timeGreeting = 'Good morning';
    mealPrompt = 'What should I cook today?';
  } else if (currentHour < 17) {
    timeGreeting = 'Good afternoon';
    mealPrompt = 'What should I cook for lunch?';
  }

  const greetingName = isGuest ? `${timeGreeting}, Chef 👋` : `${timeGreeting}, ${user?.name || 'Chef'} 👋`;
  const savedIds = (savedRecipes || []).map((r) => r.id);
  const estInventoryValue = confirmedCount > 0 ? confirmedCount * 65 : 0;
  const estimatedMealOptions = confirmedCount > 0 ? Math.max(1, Math.floor(confirmedCount * 0.8)) : 0;

  return (
    <div className="space-y-10 py-2 pb-16">
      {/* GUEST MODE BANNER IF GUEST */}
      {isGuest && (
        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-3 text-slate-300 text-xs">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              <strong className="text-white">Guest Session Active.</strong> You can explore and cook freely. Create an account anytime to save your kitchen history.
            </span>
          </div>
          <button
            onClick={() => setCurrentAuthView('signup')}
            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-xs flex items-center gap-1.5 whitespace-nowrap transition-colors shrink-0"
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>Create Account</span>
          </button>
        </div>
      )}

      {/* DASHBOARD HERO HEADER */}
      <section className="space-y-6">
        <div className="space-y-1.5">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            {greetingName}
          </h1>
          <p className="text-slate-300 text-base">
            You have <strong className="text-white font-semibold">{confirmedCount} ingredients</strong> in your kitchen.
            {urgentCount > 0 && (
              <span className="text-amber-400 font-medium"> • {urgentCount} ingredients are best used soon.</span>
            )}
          </p>
        </div>

        {/* Primary & Secondary Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={onGoToKitchenAgent}
            id="hero-cta-cook"
            className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm rounded-xl shadow-md transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>{mealPrompt}</span>
          </button>

          <button
            onClick={onStartScan}
            id="hero-cta-scan"
            className="px-5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white font-semibold text-sm rounded-xl border border-slate-700 transition-colors flex items-center gap-2"
          >
            <Camera className="w-4 h-4 text-slate-400" />
            <span>Scan my fridge</span>
          </button>

          <button
            onClick={onGoToRescue}
            id="hero-cta-rescue"
            className="px-5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white font-semibold text-sm rounded-xl border border-slate-700 transition-colors flex items-center gap-2"
          >
            <span>Rescue items</span>
          </button>
        </div>

        {/* COMPACT KITCHEN SNAPSHOT STRIP */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-5">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-3">
            Your Kitchen Today
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <div className="text-2xl font-bold text-white">{confirmedCount}</div>
              <div className="text-xs text-slate-400">ingredients</div>
            </div>
            <div>
              <div className={`text-2xl font-bold ${urgentCount > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {urgentCount}
              </div>
              <div className="text-xs text-slate-400">use soon</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-200">{estimatedMealOptions}</div>
              <div className="text-xs text-slate-400">meal options</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-emerald-400">₹{estInventoryValue}</div>
              <div className="text-xs text-slate-400">estimated value</div>
            </div>
          </div>
        </div>
      </section>

      {/* USE THESE SOON SECTION */}
      {urgentItems.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white tracking-tight">
              Use these soon
            </h2>
            <button
              onClick={onGoToRescue}
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              View all rescue items →
            </button>
          </div>

          <div className="space-y-2.5">
            {urgentItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-slate-700 transition-colors"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm">{item.name}</span>
                    <span className="text-xs text-slate-400">({item.estimated_quantity})</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      HIGH PRIORITY
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Best used in your next meal to preserve peak flavor and freshness.
                  </p>
                </div>

                <button
                  onClick={onGoToKitchenAgent}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 hover:text-emerald-300 text-xs font-semibold rounded-lg border border-slate-700 transition-colors self-start sm:self-auto"
                >
                  Cook with {item.name.toLowerCase()}
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* VEGETABLE-TO-FEAST KEY (WHAT YOU CAN MAKE FROM YOUR VEGETABLES) */}
      <VegetableDishKey
        ingredients={ingredients}
        onGenerateRecipesWithKey={() => onGoToInventory()}
        onOpenRecipeStudio={() => onGoToInventory()}
      />

      {/* TAILORED USER RECOMMENDATIONS (BASED ON SEARCHES / FRESH CHEF ESSENTIALS) */}
      <RecommendedFeasts
        recommendations={recommendations}
        isFreshUser={isFreshUser}
        onSelectRecipe={onSelectRecipe}
        onLoadIngredients={onLoadIngredientsFromRecipe}
        onSaveFavorite={onSaveFavorite}
        savedRecipeIds={savedIds}
      />

      {/* QUICK ACTIONS SECTION */}
      <section className="space-y-4">
        <h2 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <span>⚡ Quick Actions</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={onStartScan}
            id="quick-act-scan"
            className="p-5 bg-slate-900 hover:bg-slate-800/90 rounded-2xl border border-slate-800 hover:border-emerald-500/50 text-left transition-all group shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold mb-3">
                <Camera className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-base group-hover:text-emerald-400 transition-colors">
                📸 Scan Fridge
              </h3>
              <p className="text-slate-400 text-xs mt-1">"Find what's available."</p>
            </div>
            <div className="mt-4 text-xs font-bold text-emerald-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>Start Scan</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </button>

          <button
            onClick={onGoToInventory}
            id="quick-act-inventory"
            className="p-5 bg-slate-900 hover:bg-slate-800/90 rounded-2xl border border-slate-800 hover:border-emerald-500/50 text-left transition-all group shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold mb-3">
                <ListCheck className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-base group-hover:text-emerald-400 transition-colors">
                🥕 Manage Inventory
              </h3>
              <p className="text-slate-400 text-xs mt-1">"Review your ingredients."</p>
            </div>
            <div className="mt-4 text-xs font-bold text-emerald-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>View Inventory</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </button>

          <button
            onClick={onGoToRecipes}
            id="quick-act-recipes"
            className="p-5 bg-slate-900 hover:bg-slate-800/90 rounded-2xl border border-slate-800 hover:border-emerald-500/50 text-left transition-all group shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold mb-3">
                <UtensilsCrossed className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-base group-hover:text-emerald-400 transition-colors">
                🍝 Explore Recipes
              </h3>
              <p className="text-slate-400 text-xs mt-1">"Discover your next meal."</p>
            </div>
            <div className="mt-4 text-xs font-bold text-emerald-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>View Recipes</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </button>

          <button
            onClick={onGoToFeastbook}
            id="quick-act-feastbook"
            className="p-5 bg-slate-900 hover:bg-slate-800/90 rounded-2xl border border-slate-800 hover:border-emerald-500/50 text-left transition-all group shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold mb-3">
                <BookMarked className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-base group-hover:text-amber-400 transition-colors">
                ❤️ Feastbook
              </h3>
              <p className="text-slate-400 text-xs mt-1">"Open your saved recipes."</p>
            </div>
            <div className="mt-4 text-xs font-bold text-amber-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>Open Collection</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </button>
        </div>
      </section>

      {/* SAMPLE FRIDGE PRESETS FOR 1-CLICK TESTING */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              Instant Demo Presets
            </h2>
            <p className="text-slate-400 text-xs mt-0.5">
              Select a pre-configured kitchen scenario with genuine fresh ingredients to analyze immediately.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {SAMPLE_FRIDGE_PRESETS.map((preset) => (
            <div
              key={preset.id}
              onClick={() => onSelectPreset(preset)}
              id={`preset-card-${preset.id}`}
              className="group bg-slate-900 rounded-2xl border border-slate-800 p-4 shadow-sm hover:shadow-md transition-all duration-300 hover:border-emerald-500/60 cursor-pointer flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="relative h-36 rounded-xl overflow-hidden bg-slate-800">
                  <img
                    src={preset.imageUrl}
                    alt={preset.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-2 right-2 bg-slate-950/90 text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-500/30">
                    {preset.badge}
                  </div>
                </div>

                <div>
                  <h3 className="font-extrabold text-white text-sm group-hover:text-emerald-400 transition-colors">
                    {preset.title}
                  </h3>
                  <p className="text-slate-400 text-xs mt-0.5 line-clamp-2">{preset.description}</p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 mt-3 flex items-center justify-between text-emerald-400 font-bold text-xs group-hover:translate-x-1 transition-transform">
                <span>Analyze this fridge</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* RECENT FEASTS SECTION */}
      <section className="space-y-4 pt-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-extrabold text-white tracking-tight">
            Recent Feasts
          </h2>
          {recipes.length > 0 && (
            <button
              onClick={onGoToRecipes}
              className="text-xs font-bold text-emerald-400 hover:underline"
            >
              View All ({recipes.length})
            </button>
          )}
        </div>

        {recipes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recipes.slice(0, 3).map((recipe) => (
              <div
                key={recipe.id}
                className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-3 shadow-md flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs mb-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-extrabold border border-emerald-500/30">
                      {recipe.badge || 'Zero Waste'}
                    </span>
                    <span className="text-slate-400 font-medium">{recipe.cuisine}</span>
                  </div>

                  <h3 className="font-extrabold text-white text-base">
                    {recipe.title}
                  </h3>
                  <p className="text-slate-400 text-xs mt-1">
                    ⏱ {recipe.cooking_time_minutes} mins • 🍽 {recipe.servings} servings
                  </p>
                  <p className="text-emerald-400 text-xs font-bold mt-2">
                    ♻️ {recipe.ingredient_utilization_percentage}% Utilization
                  </p>
                </div>

                <button
                  onClick={() => onSelectRecipe(recipe)}
                  className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl transition-all shadow-sm flex items-center justify-center gap-1.5"
                >
                  <ChefHat className="w-3.5 h-3.5" />
                  <span>Open Recipe</span>
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-8 text-center space-y-3">
            <p className="text-slate-200 font-bold text-base">No recipes generated yet in your session.</p>
            <p className="text-slate-400 text-xs max-w-sm mx-auto">
              Scan your fridge or choose a preset to generate personalized zero-waste meals.
            </p>
            <button
              onClick={onStartScan}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md inline-flex items-center gap-2"
            >
              <Camera className="w-4 h-4" />
              <span>📸 Scan My Fridge</span>
            </button>
          </div>
        )}
      </section>
    </div>
  );
};

