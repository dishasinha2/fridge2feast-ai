import { Type } from '@google/genai';

export const INGREDIENT_VISION_SYSTEM_INSTRUCTION = `You are a highly accurate Food AI Multimodal Vision Expert for Fridge2Feast AI.
Your sole mission is to analyze photos of refrigerators, pantries, spice racks, or kitchen countertops and detect visible edible ingredients.

RULES & CONSTRAINTS:
1. ONLY identify food and drink ingredients that are visually recognizable in the photo.
2. DO NOT invent or assume ingredients that are hidden or not visible.
3. Distinguish food ingredients from non-food objects (e.g. tupperware lids, plastic wrap, refrigerator shelves, condiment bottles without clear labels, magnets, paper towels).
4. Estimate quantity and unit when reasonably possible (e.g. "3 items", "Half bottle", "1 pack", "Approx 500g").
5. Categorize each item into categories such as: Vegetable, Fruit, Dairy, Meat/Seafood, Grain/Bakery, Condiment/Sauce, Beverage, Pantry/Spice, Other.
6. Provide a numerical confidence score between 0.0 and 1.0. Assign confidence_label:
   - 0.85 - 1.00: "High"
   - 0.65 - 0.84: "Medium"
   - 0.40 - 0.64: "Low"
   - Below 0.40: Place in 'uncertain_items' array instead.
7. If non-food items are prominent (e.g., storage bins, water filter), list them briefly in 'non_food_items_detected'.

You MUST respond strictly with valid JSON.`;

export const INGREDIENT_VISION_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    ingredients: {
      type: Type.ARRAY,
      description: 'List of clearly identified food ingredients',
      items: {
        type: Type.OBJECT,
        properties: {
          name: { type: Type.STRING, description: 'Common ingredient name e.g. Tomato, Milk, Cheddar Cheese' },
          category: { type: Type.STRING, description: 'Category e.g. Vegetable, Dairy, Meat/Seafood, Grain/Bakery, Condiment/Sauce, Pantry/Spice' },
          estimated_quantity: { type: Type.STRING, description: 'Estimated visible quantity e.g. 2 items, 1/2 carton, 250g' },
          confidence: { type: Type.NUMBER, description: 'Confidence rating from 0.0 to 1.0' },
          confidence_label: { type: Type.STRING, description: 'High, Medium, Low, or Uncertain' },
        },
        required: ['name', 'category', 'estimated_quantity', 'confidence', 'confidence_label'],
      },
    },
    uncertain_items: {
      type: Type.ARRAY,
      description: 'Items that look like food but cannot be identified with high confidence',
      items: { type: Type.STRING },
    },
    non_food_items_detected: {
      type: Type.ARRAY,
      description: 'Non-food objects visible in the image e.g. Tupperware, Plastic jar, Ice tray',
      items: { type: Type.STRING },
    },
    summary: {
      type: Type.STRING,
      description: 'A friendly 1-sentence summary of the fridge analysis',
    },
  },
  required: ['ingredients', 'uncertain_items', 'non_food_items_detected'],
};

export const RECIPE_GENERATOR_SYSTEM_INSTRUCTION = `You are an Executive AI Culinary Master & Zero-Waste Food Scientist for Fridge2Feast AI.
Your objective is to generate EXACTLY 3 distinct, practical, mouthwatering recipes that maximize the use of available confirmed ingredients while keeping additional missing ingredients minimal and inexpensive.

RECIPE CATEGORIES:
1. "Best Match": Maximizes ingredient utilization from the user's available list. Uses the highest percentage of what is in their fridge.
2. "Quick Feast": Focuses on speed and convenience. Fast preparation (usually under 20-30 mins) with minimal cookware.
3. "Creative Pick": An innovative, restaurant-quality fusion or surprise dish that transforms simple leftovers into an exciting meal.

RULES & CONSTRAINTS:
1. Strict adherence to user preferences (Diet, Cuisine, Max Cooking Time, Difficulty, Servings, Budget INR, Spice Level, Dietary Restrictions).
2. Calculate realistic ingredient_utilization_percentage based on how many confirmed available ingredients are utilized.
3. For any missing ingredients, provide realistic estimated prices in INR (₹) and ensure total missing cost stays within the user's budget.
4. Step-by-step preparation steps must be clear, actionable, numbered logically, and easy to follow.
5. Provide a realistic food_waste_note explaining how this recipe reduces specific ingredient spoilage.
6. Provide smart substitutions for common allergies or alternatives.

You MUST return valid JSON adhering strictly to the schema.`;

export const RECIPE_GENERATOR_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    recipes: {
      type: Type.ARRAY,
      description: 'List of exactly 3 generated recipes',
      items: {
        type: Type.OBJECT,
        properties: {
          badge: { type: Type.STRING, description: 'Must be one of: Best Match, Quick Feast, Creative Pick' },
          title: { type: Type.STRING, description: 'Catchy culinary recipe name' },
          short_description: { type: Type.STRING, description: 'Enticing 1-2 sentence description' },
          cuisine: { type: Type.STRING, description: 'e.g. Indian, Italian, Fusion' },
          difficulty: { type: Type.STRING, description: 'Easy, Medium, or Advanced' },
          cooking_time_minutes: { type: Type.INTEGER, description: 'Total time in minutes' },
          servings: { type: Type.INTEGER, description: 'Number of servings' },
          ingredient_utilization_percentage: { type: Type.INTEGER, description: 'e.g. 85 for 85%' },
          ingredients_available: {
            type: Type.ARRAY,
            description: 'Confirmed ingredients used in this recipe',
            items: {
              type: Type.OBJECT,
              properties: {
                name: { type: Type.STRING },
                quantity: { type: Type.STRING },
                isAvailable: { type: Type.BOOLEAN },
              },
              required: ['name', 'quantity', 'isAvailable'],
            },
          },
          ingredients_missing: {
            type: Type.ARRAY,
            description: 'Pantry staples or extra ingredients required with cost in INR',
            items: {
              type: Type.OBJECT,
              properties: {
                name: { type: Type.STRING },
                estimated_quantity: { type: Type.STRING },
                estimated_price_inr: { type: Type.NUMBER },
              },
              required: ['name', 'estimated_quantity', 'estimated_price_inr'],
            },
          },
          estimated_missing_cost_inr: { type: Type.NUMBER, description: 'Total cost of missing ingredients in INR' },
          nutrition_estimate: {
            type: Type.OBJECT,
            properties: {
              calories: { type: Type.INTEGER },
              protein_g: { type: Type.INTEGER },
              carbs_g: { type: Type.INTEGER },
              fat_g: { type: Type.INTEGER },
              fiber_g: { type: Type.INTEGER },
            },
            required: ['calories', 'protein_g', 'carbs_g', 'fat_g', 'fiber_g'],
          },
          preparation_steps: {
            type: Type.ARRAY,
            items: { type: Type.STRING },
            description: 'Step by step cooking directions',
          },
          cooking_tips: {
            type: Type.ARRAY,
            items: { type: Type.STRING },
            description: 'Chef tips e.g. heat control, flavor enhancement',
          },
          substitutions: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                original: { type: Type.STRING },
                substitute: { type: Type.STRING },
                note: { type: Type.STRING },
              },
              required: ['original', 'substitute', 'note'],
            },
          },
          food_waste_note: { type: Type.STRING, description: 'Highlight on how this recipe prevents food waste' },
        },
        required: [
          'badge',
          'title',
          'short_description',
          'cuisine',
          'difficulty',
          'cooking_time_minutes',
          'servings',
          'ingredient_utilization_percentage',
          'ingredients_available',
          'ingredients_missing',
          'estimated_missing_cost_inr',
          'nutrition_estimate',
          'preparation_steps',
          'cooking_tips',
          'substitutions',
          'food_waste_note',
        ],
      },
    },
  },
  required: ['recipes'],
};
