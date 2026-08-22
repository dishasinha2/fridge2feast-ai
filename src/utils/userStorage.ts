import { UserPreferences, DetectedIngredient, Recipe, SessionHistoryItem } from '../types';

export interface UserSearchRecord {
  id: string;
  query: string;
  timestamp: string;
  categoryUsed?: string;
}

export interface UserDataFile {
  email: string;
  name: string;
  lastUpdated: string;
  preferences: UserPreferences;
  ingredients: DetectedIngredient[];
  savedRecipes: Recipe[];
  sessionHistory: SessionHistoryItem[];
  recentSearches: UserSearchRecord[];
}

export const DEFAULT_USER_PREFERENCES: UserPreferences = {
  diet: 'No Preference',
  cuisine: 'Any',
  cookingTime: 'Under 30 minutes',
  difficulty: 'Medium',
  servings: 2,
  budgetINR: 500,
  spiceLevel: 'Medium',
  dietaryRestrictions: [],
};

const getStorageKey = (email: string) => {
  const sanitized = (email || 'guest').trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
  return `f2f_user_file_${sanitized}`;
};

/**
 * Loads a user's isolated data file. If none exists, creates a fresh user profile.
 */
export function loadUserFile(email: string, displayName?: string): UserDataFile {
  const key = getStorageKey(email);
  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        email: parsed.email || email,
        name: parsed.name || displayName || 'Chef',
        lastUpdated: parsed.lastUpdated || new Date().toISOString(),
        preferences: parsed.preferences || DEFAULT_USER_PREFERENCES,
        ingredients: Array.isArray(parsed.ingredients) ? parsed.ingredients : [],
        savedRecipes: Array.isArray(parsed.savedRecipes) ? parsed.savedRecipes : [],
        sessionHistory: Array.isArray(parsed.sessionHistory) ? parsed.sessionHistory : [],
        recentSearches: Array.isArray(parsed.recentSearches) ? parsed.recentSearches : [],
      };
    }
  } catch (err) {
    console.error(`Failed to load user file for ${email}:`, err);
  }

  // Fresh user profile - completely clean, zero dump data
  const freshFile: UserDataFile = {
    email: email || 'guest@fridge2feast.ai',
    name: displayName || 'Chef',
    lastUpdated: new Date().toISOString(),
    preferences: DEFAULT_USER_PREFERENCES,
    ingredients: [],
    savedRecipes: [],
    sessionHistory: [],
    recentSearches: [],
  };

  try {
    localStorage.setItem(key, JSON.stringify(freshFile));
  } catch (err) {
    console.error(`Failed to initialize user file for ${email}:`, err);
  }

  return freshFile;
}

/**
 * Persists changes directly to the user's isolated file.
 */
export function saveUserFile(email: string, data: Partial<UserDataFile>): void {
  const key = getStorageKey(email);
  try {
    let existing: UserDataFile;
    const raw = localStorage.getItem(key);
    if (raw) {
      existing = JSON.parse(raw);
    } else {
      existing = {
        email: email || 'guest@fridge2feast.ai',
        name: 'Chef',
        lastUpdated: new Date().toISOString(),
        preferences: DEFAULT_USER_PREFERENCES,
        ingredients: [],
        savedRecipes: [],
        sessionHistory: [],
        recentSearches: [],
      };
    }

    const updated: UserDataFile = {
      ...existing,
      ...data,
      lastUpdated: new Date().toISOString(),
    };
    localStorage.setItem(key, JSON.stringify(updated));
  } catch (err) {
    console.error(`Failed to save user file for ${email}:`, err);
  }
}

/**
 * Clears only the active user's file.
 */
export function clearUserFile(email: string): void {
  const key = getStorageKey(email);
  try {
    localStorage.removeItem(key);
  } catch (err) {
    console.error(`Failed to clear user file for ${email}:`, err);
  }
}
