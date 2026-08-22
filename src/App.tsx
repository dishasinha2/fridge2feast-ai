import React, { useState, useEffect, useMemo } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar, NavTab } from './components/Navbar';
import { LandingPage } from './components/LandingPage';
import { PublicLandingPage } from './components/PublicLandingPage';
import { LoginPage } from './components/LoginPage';
import { SignupPage } from './components/SignupPage';
import { FridgeScanner } from './components/FridgeScanner';
import { IngredientReview } from './components/IngredientReview';
import { PreferencesForm } from './components/PreferencesForm';
import { RecipeResults } from './components/RecipeResults';
import { RecipeDashboard } from './components/RecipeDashboard';
import { Feastbook } from './components/Feastbook';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { KitchenAgent } from './components/KitchenAgent';
import { RescueMode } from './components/RescueMode';
import { MealPlanner } from './components/MealPlanner';
import { Lock, Sparkles, ChefHat } from 'lucide-react';

import {
  DetectedIngredient,
  UserPreferences,
  Recipe,
  SessionHistoryItem,
} from './types';
import { PresetFridge } from './data/sampleData';
import { loadUserFile, saveUserFile, DEFAULT_USER_PREFERENCES, UserDataFile } from './utils/userStorage';
import { getTailoredRecommendations } from './utils/recommendations';

function MainAppContent() {
  const { user, isAuthenticated, isGuest, currentAuthView, setCurrentAuthView, continueAsGuest } = useAuth();

  const [activeTab, setActiveTab] = useState<NavTab>('home');

  // Active user identifier
  const userIdentifier = user?.email || (isGuest ? 'guest_session' : 'unauthenticated');

  // Scanner & Vision state
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [scannerError, setScannerError] = useState<string | null>(null);
  const [detectedIngredients, setDetectedIngredients] = useState<DetectedIngredient[]>([]);
  const [uncertainItems, setUncertainItems] = useState<string[]>([]);
  const [nonFoodItems, setNonFoodItems] = useState<string[]>([]);
  const [analysisSummary, setAnalysisSummary] = useState<string>('');

  // Recipe generation state
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_USER_PREFERENCES);
  const [isGeneratingRecipes, setIsGeneratingRecipes] = useState<boolean>(false);
  const [recipeError, setRecipeError] = useState<string | null>(null);
  const [generatedRecipes, setGeneratedRecipes] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

  // Feastbook & Session history state (User-Specific)
  const [savedRecipes, setSavedRecipes] = useState<Recipe[]>([]);
  const [sessionHistory, setSessionHistory] = useState<SessionHistoryItem[]>([]);

  // Load user file whenever active user or guest state changes
  useEffect(() => {
    if (userIdentifier && userIdentifier !== 'unauthenticated') {
      const userFile = loadUserFile(userIdentifier, user?.name);
      setDetectedIngredients(userFile.ingredients || []);
      setPreferences(userFile.preferences || DEFAULT_USER_PREFERENCES);
      setSavedRecipes(userFile.savedRecipes || []);
      setSessionHistory(userFile.sessionHistory || []);
      setGeneratedRecipes([]);
      setSelectedRecipe(null);
    }
  }, [userIdentifier, user?.name]);

  // Sync state changes automatically to user's isolated file
  useEffect(() => {
    if (userIdentifier && userIdentifier !== 'unauthenticated') {
      saveUserFile(userIdentifier, {
        ingredients: detectedIngredients,
        preferences,
        savedRecipes,
        sessionHistory,
      });
    }
  }, [userIdentifier, detectedIngredients, preferences, savedRecipes, sessionHistory]);

  // Compute live user profile file representation for recommendations
  const activeUserFile: UserDataFile = useMemo(() => ({
    email: userIdentifier,
    name: user?.name || 'Chef',
    lastUpdated: new Date().toISOString(),
    preferences,
    ingredients: detectedIngredients,
    savedRecipes,
    sessionHistory,
    recentSearches: [],
  }), [userIdentifier, user?.name, preferences, detectedIngredients, savedRecipes, sessionHistory]);

  // Generate real, non-dump user recommendations
  const tailoredRecommendations = useMemo(() => {
    return getTailoredRecommendations(activeUserFile);
  }, [activeUserFile]);

  const isFreshUser = (!sessionHistory || sessionHistory.length === 0) &&
                      (!savedRecipes || savedRecipes.length === 0) &&
                      (!detectedIngredients || detectedIngredients.length === 0);

  // Handle Preset Selection (1-click instant test)
  const handleSelectPreset = (preset: PresetFridge) => {
    setDetectedIngredients(preset.sampleIngredients);
    setUncertainItems([]);
    setNonFoodItems([]);
    setAnalysisSummary(`Loaded pre-configured preset: ${preset.title}`);
    setScannerError(null);
    setActiveTab('review');
  };

  // Handle Fridge Image Analysis via Gemini API
  const handleAnalyzeImage = async (base64Image: string, mimeType: string) => {
    setIsAnalyzing(true);
    setScannerError(null);

    try {
      const response = await fetch('/api/analyze-fridge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imageBase64: base64Image, mimeType }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze fridge photo.');
      }

      setDetectedIngredients(data.ingredients || []);
      setUncertainItems(data.uncertain_items || []);
      setNonFoodItems(data.non_food_items_detected || []);
      setAnalysisSummary(data.summary || `Detected ${data.ingredients?.length || 0} ingredients.`);

      setActiveTab('review');
    } catch (err: any) {
      console.error('Error in handleAnalyzeImage:', err);
      setScannerError(err.message || 'Unable to analyze image. Please try a clearer photo.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle Recipe Generation via Gemini API
  const handleGenerateRecipes = async (userPref: UserPreferences) => {
    setIsGeneratingRecipes(true);
    setRecipeError(null);
    setPreferences(userPref);

    try {
      const confirmed = (detectedIngredients || []).filter((ing) => ing && ing.included);
      if (confirmed.length === 0) {
        throw new Error('Please select at least one confirmed ingredient.');
      }

      const response = await fetch('/api/generate-recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          confirmedIngredients: confirmed,
          preferences: userPref,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate recipes.');
      }

      const recipes: Recipe[] = data.recipes || [];
      setGeneratedRecipes(recipes);

      // Record in Session History
      const historyRecord: SessionHistoryItem = {
        id: `session-${Date.now()}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        detectedCount: confirmed.length,
        confirmedIngredients: confirmed,
        recipes,
        preferences: userPref,
      };

      setSessionHistory((prev) => [historyRecord, ...prev]);
      setSelectedRecipe(recipes[0] || null);
      setActiveTab('recipes');
    } catch (err: any) {
      console.error('Error in handleGenerateRecipes:', err);
      setRecipeError(err.message || 'Unable to generate recipes right now.');
    } finally {
      setIsGeneratingRecipes(false);
    }
  };

  // Toggle Save Favorite
  const handleToggleFavorite = (recipe: Recipe) => {
    const isAlreadySaved = (savedRecipes || []).some((r) => r.id === recipe.id);
    if (isAlreadySaved) {
      setSavedRecipes((prev) => (prev || []).filter((r) => r.id !== recipe.id));
    } else {
      const savedItem: Recipe = {
        ...recipe,
        savedAt: new Date().toLocaleDateString(),
      };
      setSavedRecipes((prev) => [savedItem, ...(prev || [])]);
    }
  };

  const handleRemoveFavorite = (id: string) => {
    setSavedRecipes((prev) => (prev || []).filter((r) => r.id !== id));
  };

  // Load ingredients into inventory from a recipe
  const handleLoadIngredientsFromRecipe = (recipe: Recipe) => {
    const newIngredients: DetectedIngredient[] = (recipe.ingredients_available || []).map((ing, idx) => ({
      id: `ing-rec-${Date.now()}-${idx}`,
      name: ing.name,
      category: 'Vegetable',
      estimated_quantity: ing.quantity,
      confidence: 0.95,
      confidence_label: 'High',
      included: true,
    }));

    setDetectedIngredients(newIngredients);
    setActiveTab('review');
  };

  const confirmedCount = (detectedIngredients || []).filter((ing) => ing && ing.included).length;

  // Render PUBLIC UNAUTHENTICATED VIEWS
  if (!isAuthenticated) {
    if (currentAuthView === 'login') {
      return <LoginPage onSwitchToSignup={() => setCurrentAuthView('signup')} />;
    }
    if (currentAuthView === 'signup') {
      return <SignupPage onSwitchToLogin={() => setCurrentAuthView('login')} />;
    }
    if (currentAuthView === 'app') {
      // Protected view fallback prompt
      return (
        <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center space-y-6 shadow-2xl">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto font-black">
              <Lock className="w-7 h-7" />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-extrabold text-white">Session Required</h2>
              <p className="text-slate-400 text-xs sm:text-sm">
                Please log in or continue as guest to access your isolated Fridge2Feast kitchen profile.
              </p>
            </div>
            <div className="space-y-3 pt-2">
              <button
                onClick={() => setCurrentAuthView('login')}
                className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-2xl shadow-xl shadow-emerald-950/50"
              >
                Log In
              </button>
              <button
                onClick={continueAsGuest}
                className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-2xl border border-slate-700 flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Continue as Guest</span>
              </button>
            </div>
          </div>
        </div>
      );
    }
    // Default Public Landing Page
    return (
      <PublicLandingPage
        onGoToFeature={(featureTab) => {
          setActiveTab(featureTab);
        }}
      />
    );
  }

  // Render AUTHENTICATED APP VIEWS
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col selection:bg-emerald-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        confirmedCount={confirmedCount}
        savedCount={(savedRecipes || []).length}
        hasRecipes={(generatedRecipes || []).length > 0}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* TAB 1: AUTHENTICATED DASHBOARD */}
        {activeTab === 'home' && (
          <LandingPage
            onStartScan={() => setActiveTab('scan')}
            onGoToInventory={() => setActiveTab('review')}
            onGoToRecipes={() => setActiveTab('recipes')}
            onGoToFeastbook={() => setActiveTab('feastbook')}
            onSelectPreset={handleSelectPreset}
            onSelectRecipe={(r) => {
              setSelectedRecipe(r);
              setActiveTab('recipes');
            }}
            onSaveFavorite={handleToggleFavorite}
            onLoadIngredientsFromRecipe={handleLoadIngredientsFromRecipe}
            ingredients={detectedIngredients || []}
            recipes={generatedRecipes || []}
            savedRecipes={savedRecipes || []}
            recommendations={tailoredRecommendations}
            isFreshUser={isFreshUser}
          />
        )}

        {/* TAB 2: FRIDGE SCANNER */}
        {activeTab === 'scan' && (
          <FridgeScanner
            onAnalyzeImage={handleAnalyzeImage}
            onSelectPreset={handleSelectPreset}
            isAnalyzing={isAnalyzing}
            error={scannerError}
          />
        )}

        {/* TAB 3: INGREDIENT REVIEW & PREFERENCES */}
        {activeTab === 'review' && (
          <div className="space-y-12">
            <IngredientReview
              ingredients={detectedIngredients}
              uncertainItems={uncertainItems}
              nonFoodItems={nonFoodItems}
              summary={analysisSummary}
              onUpdateIngredients={setDetectedIngredients}
              onConfirmAndContinue={() => {
                const prefSection = document.getElementById('preferences-form-section');
                if (prefSection) {
                  prefSection.scrollIntoView({ behavior: 'smooth' });
                }
              }}
            />

            <div id="preferences-form-section">
              {recipeError && (
                <div className="max-w-4xl mx-auto p-4 mb-6 rounded-2xl bg-rose-950/90 border border-rose-700 text-rose-200 text-sm font-semibold flex items-center justify-between gap-4 shadow-lg">
                  <div className="flex items-center gap-2">
                    <span className="text-base">⚠️</span>
                    <span>{recipeError}</span>
                  </div>
                  <button
                    onClick={() => handleGenerateRecipes(preferences)}
                    disabled={isGeneratingRecipes}
                    className="px-3 py-1.5 bg-rose-800 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition-all shrink-0"
                  >
                    Try Again
                  </button>
                </div>
              )}

              <PreferencesForm
                initialPreferences={preferences}
                onGenerateRecipes={handleGenerateRecipes}
                isGenerating={isGeneratingRecipes}
                confirmedIngredientsCount={confirmedCount}
              />
            </div>
          </div>
        )}

        {/* TAB 4: KITCHEN AGENT */}
        {activeTab === 'agent' && (
          <KitchenAgent
            ingredients={detectedIngredients || []}
            initialPreferences={preferences}
            onGenerateRecipes={handleGenerateRecipes}
            isGenerating={isGeneratingRecipes}
            confirmedIngredientsCount={confirmedCount}
            onGoToScan={() => setActiveTab('scan')}
          />
        )}

        {/* TAB 5: RESCUE MODE */}
        {activeTab === 'rescue' && (
          <RescueMode
            ingredients={detectedIngredients || []}
            onGenerateRescueRecipes={handleGenerateRecipes}
            isGenerating={isGeneratingRecipes}
            onGoToScan={() => setActiveTab('scan')}
            onUpdateIngredients={setDetectedIngredients}
          />
        )}

        {/* TAB 6: MEAL PLANNER */}
        {activeTab === 'planner' && (
          <MealPlanner
            savedRecipes={savedRecipes}
            inventory={detectedIngredients || []}
            onSelectRecipe={(r) => {
              setSelectedRecipe(r);
              setActiveTab('recipes');
            }}
            onGoToScan={() => setActiveTab('scan')}
            onGoToKitchenAgent={() => setActiveTab('agent')}
          />
        )}

        {/* TAB 7: RECIPES (RESULTS OR SELECTED RECIPE DASHBOARD) */}
        {activeTab === 'recipes' && (
          <div>
            {selectedRecipe ? (
              <RecipeDashboard
                recipe={selectedRecipe}
                preferences={preferences}
                totalConfirmedIngredientsCount={confirmedCount}
                onBackToResults={() => setSelectedRecipe(null)}
                onSaveFavorite={handleToggleFavorite}
                isSaved={savedRecipes.some((r) => r.id === selectedRecipe.id)}
              />
            ) : generatedRecipes.length > 0 ? (
              <RecipeResults
                recipes={generatedRecipes}
                onSelectRecipe={(r) => setSelectedRecipe(r)}
                onSaveFavorite={handleToggleFavorite}
                savedRecipeIds={savedRecipes.map((r) => r.id)}
                onStartScan={() => setActiveTab('scan')}
                onGoToKitchenAgent={() => setActiveTab('agent')}
              />
            ) : (
              <div className="bg-slate-900 rounded-2xl border border-slate-800 p-10 text-center space-y-4 max-w-md mx-auto my-12 shadow-xl">
                <h3 className="font-bold text-xl text-white">No Recipes Generated Yet</h3>
                <p className="text-slate-400 text-xs leading-relaxed">
                  Scan your fridge or set preferences in the Kitchen Agent to generate 3 personalized zero-waste recipes.
                </p>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <button
                    onClick={() => setActiveTab('scan')}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors"
                  >
                    Scan fridge
                  </button>
                  <button
                    onClick={() => setActiveTab('agent')}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs rounded-xl border border-slate-700 transition-colors"
                  >
                    Kitchen Agent
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 8: FEASTBOOK (SAVED RECIPES) */}
        {activeTab === 'feastbook' && (
          <Feastbook
            savedRecipes={savedRecipes}
            onOpenRecipe={(r) => {
              setSelectedRecipe(r);
              setActiveTab('recipes');
            }}
            onRemoveFavorite={handleRemoveFavorite}
            onGoToScan={() => setActiveTab('scan')}
          />
        )}

        {/* TAB 9: ANALYTICS DASHBOARD */}
        {activeTab === 'analytics' && (
          <AnalyticsDashboard
            sessionHistory={sessionHistory}
            savedCount={savedRecipes.length}
            onGoToScan={() => setActiveTab('scan')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 py-8 text-xs text-center mt-12">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-semibold text-slate-300">
            Fridge2Feast AI • Zero-Waste Culinary Intelligence
          </p>
          <p className="text-slate-500">
            Powered by Gemini Multimodal Vision API & Zero-Waste Culinary Intelligence • "Turn What's Left Into What's Next"
          </p>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainAppContent />
    </AuthProvider>
  );
}
