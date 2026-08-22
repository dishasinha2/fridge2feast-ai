import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { GoogleGenAI } from '@google/genai';
import {
  INGREDIENT_VISION_SCHEMA,
  INGREDIENT_VISION_SYSTEM_INSTRUCTION,
  RECIPE_GENERATOR_SCHEMA,
  RECIPE_GENERATOR_SYSTEM_INSTRUCTION,
} from './src/data/prompts.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Increase payload size limit for high-res fridge camera uploads (base64)
app.use(express.json({ limit: '30mb' }));

// Lazy initializer for Gemini client
function getGeminiClient(): GoogleGenAI {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error('AI service configuration is unavailable. Please check the Gemini API configuration.');
  }
  return new GoogleGenAI({
    apiKey,
    httpOptions: {
      headers: {
        'User-Agent': 'aistudio-build',
      },
    },
  });
}

// Centralized Model Validator to prevent invalid tokens/keys from being treated as model names
function resolveValidModelName(candidate?: string): string {
  if (candidate && typeof candidate === 'string' && candidate.startsWith('gemini-')) {
    return candidate.trim();
  }
  return 'gemini-2.5-flash';
}

const PRIMARY_MODEL = resolveValidModelName(process.env.GEMINI_MODEL);
const FALLBACK_MODELS = [
  PRIMARY_MODEL,
  'gemini-2.5-flash',
  'gemini-flash-latest',
  'gemini-3.7-flash',
].filter((v, i, a) => a.indexOf(v) === i);

/**
 * Robust Gemini model invoker with exponential backoff and model fallback
 */
async function generateContentWithRetry(ai: GoogleGenAI, requestPayload: any) {
  let lastError: any = null;

  for (const modelName of FALLBACK_MODELS) {
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const response = await ai.models.generateContent({
          ...requestPayload,
          model: modelName,
        });
        return response;
      } catch (err: any) {
        lastError = err;
        const errStr = (err?.message || String(err)).toLowerCase();
        const code = err?.status || err?.code;
        const isTransient =
          code === 503 ||
          code === 429 ||
          errStr.includes('503') ||
          errStr.includes('high demand') ||
          errStr.includes('unavailable') ||
          errStr.includes('rate limit') ||
          errStr.includes('quota');

        console.warn(`[Gemini Diagnostics] Model ${modelName} (attempt ${attempt + 1}) code: ${code || 'n/a'} - ${err?.message || err}`);

        if (isTransient && attempt < 2) {
          // Exponential backoff: 800ms, 1600ms
          await new Promise((resolve) => setTimeout(resolve, (attempt + 1) * 800));
          continue;
        } else {
          // Fall back to next model if available
          break;
        }
      }
    }
  }

  throw lastError;
}

function translateGeminiError(err: any): { message: string; statusCode: number; isTransient: boolean; errorCategory: string } {
  const errStr = (err?.message || String(err)).toLowerCase();
  const code = Number(err?.status || err?.code) || 500;

  if (code === 503 || errStr.includes('503') || errStr.includes('high demand') || errStr.includes('unavailable')) {
    return {
      message: '✨ Gemini is temporarily busy. Please try again in a moment.',
      statusCode: 503,
      isTransient: true,
      errorCategory: 'SERVICE_UNAVAILABLE',
    };
  }
  if (code === 429 || errStr.includes('429') || errStr.includes('quota') || errStr.includes('rate limit')) {
    return {
      message: '✨ AI usage is temporarily limited. Please try again shortly.',
      statusCode: 429,
      isTransient: true,
      errorCategory: 'RATE_LIMITED',
    };
  }
  if (code === 401 || code === 403 || errStr.includes('api_key') || errStr.includes('unauthenticated') || errStr.includes('permission')) {
    return {
      message: 'AI service configuration is unavailable. Please check the Gemini API configuration.',
      statusCode: 401,
      isTransient: false,
      errorCategory: 'AUTHENTICATION_REQUIRED',
    };
  }
  if (code === 408 || errStr.includes('timeout') || errStr.includes('timed out') || errStr.includes('deadline')) {
    return {
      message: 'The AI request timed out. Please try again.',
      statusCode: 408,
      isTransient: true,
      errorCategory: 'TIMEOUT',
    };
  }
  if (code === 422 || errStr.includes('validation') || errStr.includes('schema') || errStr.includes('json')) {
    return {
      message: 'The AI response could not be validated. Please try again.',
      statusCode: 422,
      isTransient: false,
      errorCategory: 'VALIDATION_ERROR',
    };
  }
  return {
    message: '✨ The AI service is currently unavailable. Please try again in a moment.',
    statusCode: code >= 400 && code < 600 ? code : 500,
    isTransient: true,
    errorCategory: 'INTERNAL_ERROR',
  };
}

// ==========================================
// API ENDPOINT 0: GEMINI HEALTH CHECK
// ==========================================
app.get('/api/gemini-health', async (req, res) => {
  const startTime = Date.now();
  const apiKeyConfigured = Boolean(process.env.GEMINI_API_KEY);

  if (!apiKeyConfigured) {
    return res.status(401).json({
      status: 'CONFIG_MISSING',
      message: 'GEMINI_API_KEY is not configured in the environment.',
      model: PRIMARY_MODEL,
      latencyMs: 0,
      apiKeyConfigured: false,
    });
  }

  try {
    const ai = getGeminiClient();
    const response = await ai.models.generateContent({
      model: PRIMARY_MODEL,
      contents: 'Respond with exactly: {"status":"healthy"}',
      config: {
        responseMimeType: 'application/json',
        temperature: 0.1,
      },
    });

    const latencyMs = Date.now() - startTime;
    return res.json({
      status: 'HEALTHY',
      model: PRIMARY_MODEL,
      latencyMs,
      apiKeyConfigured: true,
      responseSample: response.text?.slice(0, 100) || '',
      fallbackModels: FALLBACK_MODELS,
    });
  } catch (err: any) {
    const latencyMs = Date.now() - startTime;
    const translated = translateGeminiError(err);
    return res.status(translated.statusCode).json({
      status: 'UNAVAILABLE',
      error: translated.message,
      errorCategory: translated.errorCategory,
      statusCode: translated.statusCode,
      model: PRIMARY_MODEL,
      latencyMs,
      apiKeyConfigured: true,
      rawErrorSnippet: (err?.message || String(err)).slice(0, 200),
    });
  }
});

// ==========================================
// API ENDPOINT 1: FRIDGE VISION ANALYSIS
// ==========================================
app.post('/api/analyze-fridge', async (req, res) => {
  try {
    const { imageBase64, mimeType } = req.body;

    if (!imageBase64) {
      return res.status(400).json({ error: 'No image data provided. Please upload or take a photo.' });
    }

    // Clean base64 string if data URL prefix exists
    const cleanBase64 = imageBase64.replace(/^data:image\/\w+;base64,/, '');
    const actualMimeType = mimeType || 'image/jpeg';

    const imagePart = {
      inlineData: {
        mimeType: actualMimeType,
        data: cleanBase64,
      },
    };

    const textPart = {
      text: 'Examine this photo carefully. Identify all visible edible ingredients, vegetables, fruits, condiments, dairy, meats, grains, beverages, and pantry items. Exclude non-food containers and shelves. Estimate quantity, category, and confidence level for each item.',
    };

    let responseText = '{}';
    try {
      const ai = getGeminiClient();
      const response = await generateContentWithRetry(ai, {
        contents: { parts: [imagePart, textPart] },
        config: {
          systemInstruction: INGREDIENT_VISION_SYSTEM_INSTRUCTION,
          responseMimeType: 'application/json',
          responseSchema: INGREDIENT_VISION_SCHEMA,
          temperature: 0.2,
        },
      });
      responseText = response.text || '{}';
    } catch (aiErr: any) {
      console.error('Gemini vision call failed after all retries:', aiErr?.message);
      const translated = translateGeminiError(aiErr);
      return res.status(translated.statusCode).json({
        error: translated.message,
        isTransient: translated.isTransient,
      });
    }

    let parsedData;
    try {
      parsedData = JSON.parse(responseText);
    } catch (err) {
      console.error('Failed to parse Gemini Vision JSON output:', responseText);
      return res.status(500).json({
        error: 'Failed to process AI vision output. Please try again with a clearer image.',
      });
    }

    // Format output with unique IDs and default included flag
    const ingredients = (parsedData.ingredients || []).map((item: any, idx: number) => ({
      id: `detected-${Date.now()}-${idx}`,
      name: item.name || 'Unknown Ingredient',
      category: item.category || 'Pantry/Spice',
      estimated_quantity: item.estimated_quantity || '1 item',
      confidence: typeof item.confidence === 'number' ? item.confidence : 0.85,
      confidence_label: item.confidence_label || 'High',
      included: true,
    }));

    return res.json({
      ingredients,
      uncertain_items: parsedData.uncertain_items || [],
      non_food_items_detected: parsedData.non_food_items_detected || [],
      summary: parsedData.summary || `Detected ${ingredients.length} food items in your fridge photo.`,
    });
  } catch (error: any) {
    console.error('Error in /api/analyze-fridge:', error);
    const translated = translateGeminiError(error);
    return res.status(translated.statusCode).json({
      error: translated.message,
      isTransient: translated.isTransient,
    });
  }
});

// ==========================================
// API ENDPOINT 2: RECIPE GENERATION ENGINE
// ==========================================
app.post('/api/generate-recipes', async (req, res) => {
  try {
    const { confirmedIngredients, preferences } = req.body;

    if (!confirmedIngredients || !Array.isArray(confirmedIngredients) || confirmedIngredients.length === 0) {
      return res.status(400).json({ error: 'Please confirm at least one ingredient before generating recipes.' });
    }

    const availableIngredientsSummary = confirmedIngredients
      .filter((ing: any) => ing.included)
      .map((ing: any) => `- ${ing.name} (Quantity: ${ing.estimated_quantity || 'as available'}, Category: ${ing.category || 'General'})`)
      .join('\n');

    const budgetVal = preferences?.budgetINR !== undefined && preferences?.budgetINR !== null ? Number(preferences.budgetINR) : 500;
    const servingsVal = preferences?.servings !== undefined && preferences?.servings !== null ? Number(preferences.servings) : 2;
    const spiceVal = preferences?.spiceLevel !== undefined && preferences?.spiceLevel !== null ? String(preferences.spiceLevel) : 'Medium';
    const dietVal = preferences?.diet || 'No Preference';
    const cuisineVal = preferences?.cuisine || 'Any';
    const cookingTimeVal = preferences?.cookingTime || 'Under 30 minutes';
    const difficultyVal = preferences?.difficulty || 'Medium';
    const restrictionsVal = Array.isArray(preferences?.dietaryRestrictions) && preferences.dietaryRestrictions.length > 0
      ? preferences.dietaryRestrictions.join(', ')
      : 'None';

    const promptText = `
CONFIRMED AVAILABLE INGREDIENTS IN USER'S FRIDGE:
${availableIngredientsSummary || 'None explicitly marked as available.'}

USER COOKING PREFERENCES:
- Dietary Choice: ${dietVal}
- Cuisine Style: ${cuisineVal}
- Maximum Cooking Time: ${cookingTimeVal}
- Preferred Difficulty: ${difficultyVal}
- Servings: ${servingsVal}
- Maximum Missing Ingredients Budget: ₹${budgetVal} INR
- Spice Preference: ${spiceVal}
- Dietary Restrictions / Allergies: ${restrictionsVal}

TASK:
Generate EXACTLY 3 recipes tailored to these inputs:
Recipe 1 Badge: "Best Match" (Maximizes use of available ingredients above)
Recipe 2 Badge: "Quick Feast" (Easiest and fastest preparation time)
Recipe 3 Badge: "Creative Pick" (Innovative flavor combination or fusion recipe)

Ensure all costs are in Indian Rupees (INR ₹). Keep ingredient_utilization_percentage realistic.
`;

    let responseText = '{}';
    try {
      const ai = getGeminiClient();
      const response = await generateContentWithRetry(ai, {
        contents: promptText,
        config: {
          systemInstruction: RECIPE_GENERATOR_SYSTEM_INSTRUCTION,
          responseMimeType: 'application/json',
          responseSchema: RECIPE_GENERATOR_SCHEMA,
          temperature: 0.4,
        },
      });
      responseText = response.text || '{}';
    } catch (aiErr: any) {
      console.error('Gemini recipe generator call failed after retries:', aiErr?.message);
      const translated = translateGeminiError(aiErr);
      return res.status(translated.statusCode).json({
        error: translated.message,
        isTransient: translated.isTransient,
      });
    }

    let parsedData;
    try {
      parsedData = JSON.parse(responseText);
    } catch (err) {
      console.error('Failed to parse Gemini Recipe JSON output:', responseText);
      return res.status(500).json({
        error: 'Failed to format recipes. Please try submitting your preferences again.',
      });
    }

    const recipes = (parsedData.recipes || []).map((recipe: any, idx: number) => ({
      id: `recipe-${Date.now()}-${idx}`,
      badge: recipe.badge || (idx === 0 ? 'Best Match' : idx === 1 ? 'Quick Feast' : 'Creative Pick'),
      title: recipe.title || 'Delicious Homemade Dish',
      short_description: recipe.short_description || 'A tasty meal created from your fridge ingredients.',
      cuisine: recipe.cuisine || preferences?.cuisine || 'Fusion',
      difficulty: recipe.difficulty || 'Easy',
      cooking_time_minutes: recipe.cooking_time_minutes !== undefined && !isNaN(Number(recipe.cooking_time_minutes)) ? Number(recipe.cooking_time_minutes) : 25,
      servings: recipe.servings !== undefined && !isNaN(Number(recipe.servings)) ? Number(recipe.servings) : (servingsVal || 2),
      ingredient_utilization_percentage: recipe.ingredient_utilization_percentage !== undefined && !isNaN(Number(recipe.ingredient_utilization_percentage)) ? Number(recipe.ingredient_utilization_percentage) : 85,
      ingredients_available: Array.isArray(recipe.ingredients_available) ? recipe.ingredients_available : [],
      ingredients_missing: Array.isArray(recipe.ingredients_missing) ? recipe.ingredients_missing : [],
      estimated_missing_cost_inr: recipe.estimated_missing_cost_inr !== undefined && !isNaN(Number(recipe.estimated_missing_cost_inr)) ? Number(recipe.estimated_missing_cost_inr) : 0,
      nutrition_estimate: recipe.nutrition_estimate || {
        calories: 450,
        protein_g: 22,
        carbs_g: 50,
        fat_g: 16,
        fiber_g: 7,
      },
      preparation_steps: Array.isArray(recipe.preparation_steps) ? recipe.preparation_steps : [],
      cooking_tips: Array.isArray(recipe.cooking_tips) ? recipe.cooking_tips : [],
      substitutions: Array.isArray(recipe.substitutions) ? recipe.substitutions : [],
      food_waste_note: recipe.food_waste_note || 'Utilizes leftover ingredients efficiently to reduce waste.',
    }));

    return res.json({ recipes });
  } catch (error: any) {
    console.error('Error in /api/generate-recipes:', error);
    const translated = translateGeminiError(error);
    return res.status(translated.statusCode).json({
      error: translated.message,
      isTransient: translated.isTransient,
    });
  }
});

// ==========================================
// API ENDPOINT 3: CONTEXTUAL RECIPE AI SOUS-CHEF
// ==========================================
app.post('/api/recipe-assistant', async (req, res) => {
  try {
    const { recipe, userQuestion } = req.body;

    if (!userQuestion || typeof userQuestion !== 'string') {
      return res.status(400).json({ error: 'Please enter a valid question.' });
    }

    const recipeContext = recipe
      ? `
CURRENT SELECTED RECIPE:
Title: ${recipe.title}
Cuisine: ${recipe.cuisine}
Time: ${recipe.cooking_time_minutes} mins
Servings: ${recipe.servings}
Available Ingredients: ${(recipe.ingredients_available || []).map((i: any) => `${i.name} (${i.quantity})`).join(', ')}
Missing Ingredients: ${(recipe.ingredients_missing || []).map((m: any) => m.name).join(', ')}
Cooking Steps:
${(recipe.preparation_steps || []).map((s: string, idx: number) => `${idx + 1}. ${s}`).join('\n')}
`
      : 'No specific recipe selected yet.';

    const systemPrompt = `You are Fridge2Feast AI's expert personal kitchen assistant and AI Sous-Chef.
You provide encouraging, practical, concise, and helpful culinary answers.

RULES:
1. Focus directly on answering the user's specific question using the provided Recipe context.
2. If asked for substitutions, suggest 2-3 accessible everyday kitchen alternatives.
3. If asked about dietary adjustments (e.g. higher protein, vegan swap, lower sodium, spice reduction, no oven), give clear step-by-step instructions.
4. Keep answers under 180 words, formatted cleanly with bullet points if necessary.`;

    const promptText = `${recipeContext}

USER'S QUESTION:
"${userQuestion}"

Answer concise and helpfully as an expert chef:`;

    try {
      const ai = getGeminiClient();
      const response = await generateContentWithRetry(ai, {
        contents: promptText,
        config: {
          systemInstruction: systemPrompt,
          temperature: 0.5,
        },
      });

      return res.json({ answer: response.text || 'I recommend adjusting the heat and seasoning to taste.' });
    } catch (aiErr: any) {
      console.warn('AI Sous-Chef live call failed:', aiErr?.message);
      const translated = translateGeminiError(aiErr);
      return res.json({
        answer: translated.message,
      });
    }
  } catch (error: any) {
    console.error('Error in /api/recipe-assistant:', error);
    return res.status(500).json({
      error: 'Unable to get answer from AI Sous-Chef right now.',
    });
  }
});

// ==========================================
// VITE MIDDLEWARE / PRODUCTION STATIC SERVING
// ==========================================
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(__dirname, 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Fridge2Feast AI server running at http://0.0.0.0:${PORT}`);
  });
}

startServer();
