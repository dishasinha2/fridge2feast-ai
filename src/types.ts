export interface DetectedIngredient {
  id: string;
  name: string;
  category: string;
  estimated_quantity: string;
  confidence: number;
  confidence_label: 'High' | 'Medium' | 'Low' | 'Uncertain';
  included: boolean;
}

export interface VisionAnalysisResult {
  ingredients: DetectedIngredient[];
  uncertain_items: string[];
  non_food_items_detected: string[];
  summary?: string;
}

export type DietPreference =
  | 'Vegetarian'
  | 'Vegan'
  | 'Non-Vegetarian'
  | 'Eggetarian'
  | 'No Preference';

export type CuisinePreference =
  | 'Indian'
  | 'Italian'
  | 'Mexican'
  | 'Asian'
  | 'Mediterranean'
  | 'American'
  | 'Fusion'
  | 'Any';

export type CookingTimePreference =
  | 'Under 15 minutes'
  | 'Under 30 minutes'
  | 'Under 60 minutes'
  | 'No limit';

export type DifficultyPreference = 'Easy' | 'Medium' | 'Advanced';

export type SpiceLevelPreference = 'Mild' | 'Medium' | 'Spicy';

export interface UserPreferences {
  diet: DietPreference;
  cuisine: CuisinePreference;
  cookingTime: CookingTimePreference;
  difficulty: DifficultyPreference;
  servings: number;
  budgetINR: number;
  spiceLevel: SpiceLevelPreference;
  dietaryRestrictions: string[];
}

export interface RecipeIngredient {
  name: string;
  quantity: string;
  isAvailable: boolean;
}

export interface MissingIngredient {
  name: string;
  estimated_quantity: string;
  estimated_price_inr: number;
}

export interface NutritionEstimate {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}

export interface Substitution {
  original: string;
  substitute: string;
  note: string;
}

export interface Recipe {
  id: string;
  badge: 'Best Match' | 'Quick Feast' | 'Creative Pick';
  title: string;
  short_description: string;
  cuisine: string;
  difficulty: 'Easy' | 'Medium' | 'Advanced';
  cooking_time_minutes: number;
  servings: number;
  ingredient_utilization_percentage: number;
  ingredients_available: RecipeIngredient[];
  ingredients_missing: MissingIngredient[];
  estimated_missing_cost_inr: number;
  nutrition_estimate: NutritionEstimate;
  preparation_steps: string[];
  cooking_tips: string[];
  substitutions: Substitution[];
  food_waste_note: string;
  savedAt?: string;
}

export interface RecipeAiChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export interface SessionHistoryItem {
  id: string;
  timestamp: string;
  imagePreviewUrl?: string;
  detectedCount: number;
  confirmedIngredients: DetectedIngredient[];
  recipes: Recipe[];
  preferences: UserPreferences;
}

export interface AnalyticsStats {
  totalScans: number;
  totalRecipesGenerated: number;
  averageUtilization: number;
  topCategories: { category: string; count: number }[];
  favoriteCuisines: { cuisine: string; count: number }[];
  totalShoppingCostINR: number;
}
