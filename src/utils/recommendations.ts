import { Recipe } from '../types';
import { UserDataFile } from './userStorage';

export interface RecommendationCardData {
  id: string;
  badge: string;
  rationale: string;
  recipe: Recipe;
}

/**
 * Standard fresh user edible meals (100% wholesome, real ingredients, simple to cook)
 */
export const FRESH_USER_RECOMMENDED_MEALS: RecommendationCardData[] = [
  {
    id: 'fresh-rec-1',
    badge: 'Beginner Friendly',
    rationale: 'A quick, foolproof 15-minute Italian staple that uses everyday pantry ingredients.',
    recipe: {
      id: 'fresh-meal-pasta',
      badge: 'Best Match',
      title: '15-Minute Garlic Herb Penne Bowl',
      short_description: 'Tender penne pasta tossed in golden extra virgin olive oil, fragrant minced garlic, blistered cherry tomatoes, and aromatic herbs.',
      cuisine: 'Italian',
      difficulty: 'Easy',
      cooking_time_minutes: 15,
      servings: 2,
      ingredient_utilization_percentage: 95,
      ingredients_available: [
        { name: 'Penne or Spaghetti Pasta', quantity: '200g', isAvailable: true },
        { name: 'Fresh Garlic Cloves', quantity: '4 cloves, sliced', isAvailable: true },
        { name: 'Cherry or Regular Tomatoes', quantity: '1 cup, halved', isAvailable: true },
        { name: 'Olive Oil or Butter', quantity: '2 tbsp', isAvailable: true },
      ],
      ingredients_missing: [
        { name: 'Fresh Basil or Dried Oregano', estimated_quantity: '1 tsp', estimated_price_inr: 10 },
        { name: 'Parmesan or Cheese (Optional)', estimated_quantity: '2 tbsp', estimated_price_inr: 25 },
      ],
      estimated_missing_cost_inr: 35,
      nutrition_estimate: { calories: 360, protein_g: 11, carbs_g: 58, fat_g: 10, fiber_g: 4 },
      preparation_steps: [
        'Boil pasta in well-salted water for 9-10 minutes until al dente. Reserve 1/4 cup pasta water.',
        'Heat 2 tbsp olive oil in a wide pan over low-medium heat. Add sliced garlic and cook gently for 90 seconds until fragrant.',
        'Add halved tomatoes and a pinch of salt. Sauté for 3 minutes until tomatoes burst slightly.',
        'Toss drained pasta and 2 tbsp pasta water directly into the garlic pan. Toss vigorously for 1 minute.',
        'Garnish with freshly cracked black pepper and herbs before serving warm.',
      ],
      cooking_tips: [
        'Do not let the garlic brown excessively to avoid bitterness.',
        'Adding starchy pasta water emulsifies the olive oil into a silky sauce.',
      ],
      substitutions: [
        { original: 'Penne Pasta', substitute: 'Macaroni, spaghetti, or rice noodles', note: 'Any pasta shape works smoothly.' },
      ],
      food_waste_note: 'Uses overripe or soft tomatoes perfectly as they break down into a sweet sauce.',
    },
  },
  {
    id: 'fresh-rec-2',
    badge: 'High Protein',
    rationale: 'A nutrient-packed homestyle skillet that transforms fresh cottage cheese and crunchy peppers into a restaurant-style meal.',
    recipe: {
      id: 'fresh-meal-paneer',
      badge: 'Quick Feast',
      title: 'Homestyle Spiced Paneer & Pepper Sauté',
      short_description: 'Succulent cubes of paneer pan-seared with crisp bell peppers, red onions, cumin, and mild aromatic spices.',
      cuisine: 'Indian',
      difficulty: 'Easy',
      cooking_time_minutes: 20,
      servings: 2,
      ingredient_utilization_percentage: 90,
      ingredients_available: [
        { name: 'Paneer (Cottage Cheese) or Tofu', quantity: '200g cubed', isAvailable: true },
        { name: 'Green & Red Bell Peppers', quantity: '2 medium, diced', isAvailable: true },
        { name: 'Red Onions', quantity: '1 large, sliced', isAvailable: true },
        { name: 'Cooking Oil', quantity: '1.5 tbsp', isAvailable: true },
      ],
      ingredients_missing: [
        { name: 'Garam Masala & Turmeric', estimated_quantity: '1/2 tsp each', estimated_price_inr: 10 },
        { name: 'Fresh Coriander', estimated_quantity: 'Small bunch', estimated_price_inr: 5 },
      ],
      estimated_missing_cost_inr: 15,
      nutrition_estimate: { calories: 340, protein_g: 22, carbs_g: 14, fat_g: 22, fiber_g: 4 },
      preparation_steps: [
        'Heat 1 tbsp oil in a non-stick pan over medium heat. Lightly sear paneer cubes for 2-3 minutes until lightly golden. Set aside.',
        'In the same pan, add remaining oil and sauté sliced onions for 2 minutes until translucent.',
        'Add diced bell peppers and sauté on high heat for 3-4 minutes to keep them crisp.',
        'Stir in turmeric, garam masala, salt, and black pepper. Mix well.',
        'Return paneer cubes to the pan, toss for 2 minutes to coat with spices, and garnish with fresh coriander and lemon juice.',
      ],
      cooking_tips: [
        'Keep heat high when tossing peppers so they retain their crisp crunch.',
        'Soak paneer in warm water for 5 minutes before cooking for ultra-soft texture.',
      ],
      substitutions: [
        { original: 'Paneer', substitute: 'Firm Tofu or boiled chickpeas', note: 'Provides excellent plant-based protein.' },
      ],
      food_waste_note: 'Great way to utilize leftover capsicum halves and open paneer packs before they spoil.',
    },
  },
  {
    id: 'fresh-rec-3',
    badge: 'Comfort Classic',
    rationale: 'A colorful, zero-fuss skillet scramble that turns miscellaneous kitchen vegetables into a protein-rich feast.',
    recipe: {
      id: 'fresh-meal-scramble',
      badge: 'Creative Pick',
      title: 'Farmhouse Vegetable Scramble & Crisp Toast',
      short_description: 'Fluffy eggs (or seasoned tofu) folded with diced tomatoes, spinach, onions, and melted cheese served with crisp buttered toast.',
      cuisine: 'Continental',
      difficulty: 'Easy',
      cooking_time_minutes: 12,
      servings: 2,
      ingredient_utilization_percentage: 92,
      ingredients_available: [
        { name: 'Eggs or Silken Tofu', quantity: '4 whole eggs', isAvailable: true },
        { name: 'Spinach or Leafy Greens', quantity: '1 cup chopped', isAvailable: true },
        { name: 'Tomatoes', quantity: '1 medium, diced', isAvailable: true },
        { name: 'Whole Wheat Bread', quantity: '4 slices', isAvailable: true },
      ],
      ingredients_missing: [
        { name: 'Butter or Ghee', estimated_quantity: '1 tbsp', estimated_price_inr: 15 },
        { name: 'Salt & Black Pepper', estimated_quantity: 'To taste', estimated_price_inr: 5 },
      ],
      estimated_missing_cost_inr: 20,
      nutrition_estimate: { calories: 310, protein_g: 19, carbs_g: 28, fat_g: 14, fiber_g: 5 },
      preparation_steps: [
        'Whisk eggs in a bowl with a pinch of salt and black pepper until frothy.',
        'Melt 1/2 tbsp butter in a non-stick skillet over medium-low heat.',
        'Add diced tomatoes and chopped spinach. Cook for 90 seconds until spinach wilts.',
        'Pour whisked eggs into the pan. Slowly stir with a spatula from edges to center to create soft, tender curds.',
        'Remove from heat while eggs are still soft and glossy. Serve with golden toasted whole wheat bread.',
      ],
      cooking_tips: [
        'Cook on gentle low heat to keep eggs tender and prevent rubbery texture.',
      ],
      substitutions: [
        { original: 'Eggs', substitute: 'Crumbled tofu with a pinch of turmeric', note: 'Creates an authentic, delicious vegan scramble.' },
      ],
      food_waste_note: 'Utilizes small remaining handfuls of spinach and soft tomatoes before they wilt.',
    },
  },
];

/**
 * Computes recommendations tailored to user's specific history, searches, and inventory
 */
export function getTailoredRecommendations(userFile: UserDataFile): RecommendationCardData[] {
  const { sessionHistory, savedRecipes, ingredients, preferences } = userFile;

  // If user has no sessions, saved recipes, or scanned ingredients, return clean fresh essentials
  const isFresh = (!sessionHistory || sessionHistory.length === 0) &&
                  (!savedRecipes || savedRecipes.length === 0) &&
                  (!ingredients || ingredients.length === 0);

  if (isFresh) {
    return FRESH_USER_RECOMMENDED_MEALS;
  }

  // Analyze active ingredients and past searches
  const ingredientNames = (ingredients || []).map((i) => i.name.toLowerCase());
  const hasPaneerOrCheese = ingredientNames.some((n) => n.includes('paneer') || n.includes('cheese'));
  const hasTomatoes = ingredientNames.some((n) => n.includes('tomato'));
  const hasPeppers = ingredientNames.some((n) => n.includes('pepper') || n.includes('capsicum'));
  const hasRiceOrPasta = ingredientNames.some((n) => n.includes('rice') || n.includes('pasta') || n.includes('noodle'));
  const hasEggs = ingredientNames.some((n) => n.includes('egg'));
  const hasGreens = ingredientNames.some((n) => n.includes('spinach') || n.includes('palak') || n.includes('broccoli'));

  const tailored: RecommendationCardData[] = [];

  // Tailored 1: Based on active vegetable ingredients
  if (hasTomatoes && hasPeppers) {
    tailored.push({
      id: 'tailored-shakshuka',
      badge: 'Pantry Match',
      rationale: `Recommended because you have fresh Tomatoes and Bell Peppers ready in your kitchen.`,
      recipe: {
        id: 'rec-shakshuka',
        badge: 'Best Match',
        title: 'Rustic Spiced Tomato & Pepper Shakshuka',
        short_description: 'Gently simmered rich tomato and sweet bell pepper stew infused with cumin and garlic, topped with soft eggs or paneer cubes.',
        cuisine: 'Mediterranean',
        difficulty: 'Easy',
        cooking_time_minutes: 20,
        servings: preferences?.servings || 2,
        ingredient_utilization_percentage: 92,
        ingredients_available: [
          { name: 'Tomatoes', quantity: '3 large, chopped', isAvailable: true },
          { name: 'Bell Peppers', quantity: '2 diced', isAvailable: true },
          { name: 'Onions & Garlic', quantity: '1 onion, 3 cloves garlic', isAvailable: true },
          { name: 'Eggs or Paneer', quantity: '3-4 eggs or 150g paneer', isAvailable: true },
        ],
        ingredients_missing: [
          { name: 'Ground Cumin & Paprika', estimated_quantity: '1 tsp each', estimated_price_inr: 15 },
          { name: 'Crusty Bread', estimated_quantity: '4 slices', estimated_price_inr: 25 },
        ],
        estimated_missing_cost_inr: 40,
        nutrition_estimate: { calories: 340, protein_g: 18, carbs_g: 26, fat_g: 16, fiber_g: 6 },
        preparation_steps: [
          'Heat 1 tbsp olive oil in a skillet. Sauté onions and bell peppers for 5 minutes until tender.',
          'Add minced garlic, cumin, and paprika. Cook for 1 minute until fragrant.',
          'Pour in chopped tomatoes with salt and black pepper. Simmer for 10 minutes until sauce thickens.',
          'Make small wells in the sauce. Crack eggs (or nestle paneer cubes) into wells.',
          'Cover and simmer on low for 5-7 minutes until egg whites are set but yolks remain runny. Serve with toasted bread.',
        ],
        cooking_tips: ['Covering the pan traps steam, cooking egg whites evenly without overcooking yolks.'],
        substitutions: [{ original: 'Eggs', substitute: 'Soft tofu or paneer cubes', note: 'Perfect plant-based alternative.' }],
        food_waste_note: 'Uses ripe tomatoes and bell peppers that need immediate cooking.',
      },
    });
  }

  // Tailored 2: Quick Rice / Grain Feast
  if (hasRiceOrPasta || tailored.length < 2) {
    tailored.push({
      id: 'tailored-fried-rice',
      badge: 'Zero-Waste Favorite',
      rationale: `Perfect for utilizing yesterday's leftover cooked grains with your crisp vegetables.`,
      recipe: {
        id: 'rec-fried-rice',
        badge: 'Quick Feast',
        title: 'Golden Garlic Veggie Wok Rice',
        short_description: 'High-heat wok-tossed rice with crunchy carrots, green peas, spring onions, and a splash of toasted sesame oil and soy sauce.',
        cuisine: 'Asian',
        difficulty: 'Easy',
        cooking_time_minutes: 15,
        servings: preferences?.servings || 2,
        ingredient_utilization_percentage: 88,
        ingredients_available: [
          { name: 'Cooked Rice or Grains', quantity: '2-3 cups chilled', isAvailable: true },
          { name: 'Mixed Vegetables (Carrots, Beans, Peas)', quantity: '1.5 cups finely diced', isAvailable: true },
          { name: 'Garlic & Spring Onions', quantity: '3 cloves + 2 stalks', isAvailable: true },
        ],
        ingredients_missing: [
          { name: 'Soy Sauce', estimated_quantity: '1.5 tbsp', estimated_price_inr: 15 },
          { name: 'Toasted Sesame Seeds/Oil', estimated_quantity: '1 tsp', estimated_price_inr: 15 },
        ],
        estimated_missing_cost_inr: 30,
        nutrition_estimate: { calories: 370, protein_g: 9, carbs_g: 65, fat_g: 8, fiber_g: 5 },
        preparation_steps: [
          'Heat 1 tbsp oil in a wide wok over high heat until shimmering.',
          'Add minced garlic and whites of spring onions. Sauté for 30 seconds.',
          'Toss in diced mixed vegetables. Stir-fry briskly for 3 minutes until tender-crisp.',
          'Add cold cooked rice, breaking up any clumps with a spatula.',
          'Drizzle soy sauce, pepper, and a pinch of salt around the edges of the wok. Toss for 2 minutes to caramelize.',
          'Garnish with green spring onion tops and serve steaming hot.',
        ],
        cooking_tips: ['Chilled day-old rice fries crisply without becoming mushy.'],
        substitutions: [{ original: 'Soy Sauce', substitute: 'Tamari or Coconut Aminos', note: 'Gluten-free option.' }],
        food_waste_note: 'Prevents cooked rice from going to waste while clearing odd vegetable odds and ends.',
      },
    });
  }

  // Tailored 3: Green antioxidant power
  if (hasGreens || hasPaneerOrCheese || tailored.length < 3) {
    tailored.push({
      id: 'tailored-palak-paneer',
      badge: 'Nutrient Rich',
      rationale: `Matched to your healthy preference for leafy greens and wholesome proteins.`,
      recipe: {
        id: 'rec-palak-skillet',
        badge: 'Creative Pick',
        title: 'Creamy Spiced Spinach & Paneer Skillet',
        short_description: 'Vibrant emerald spinach purée gently spiced with cumin, ginger, and garlic, gently embracing pan-seared paneer cubes.',
        cuisine: 'Indian',
        difficulty: 'Medium',
        cooking_time_minutes: 25,
        servings: preferences?.servings || 2,
        ingredient_utilization_percentage: 94,
        ingredients_available: [
          { name: 'Fresh Spinach (Palak)', quantity: '1 large bunch (300g)', isAvailable: true },
          { name: 'Paneer or Tofu', quantity: '200g cubed', isAvailable: true },
          { name: 'Ginger & Garlic Paste', quantity: '1 tbsp', isAvailable: true },
          { name: 'Onions & Green Chili', quantity: '1 medium onion, 1 chili', isAvailable: true },
        ],
        ingredients_missing: [
          { name: 'Garam Masala & Cumin Seeds', estimated_quantity: '1 tsp', estimated_price_inr: 10 },
          { name: 'Fresh Cream or Yogurt', estimated_quantity: '2 tbsp', estimated_price_inr: 20 },
        ],
        estimated_missing_cost_inr: 30,
        nutrition_estimate: { calories: 360, protein_g: 24, carbs_g: 12, fat_g: 24, fiber_g: 6 },
        preparation_steps: [
          'Blanch spinach in boiling water for 2 minutes, then transfer to cold water to retain vibrant green color. Blend into a smooth purée.',
          'Pan-sear paneer cubes in 1/2 tbsp ghee/oil for 3 minutes until lightly golden. Set aside.',
          'In the same skillet, crackle cumin seeds, then sauté chopped onions and ginger-garlic paste until golden.',
          'Pour in the blended spinach purée with salt, garam masala, and 2 tbsp cream/yogurt. Simmer for 4 minutes.',
          'Fold in seared paneer cubes and simmer gently for 2 minutes before serving with roti or rice.',
        ],
        cooking_tips: ['Blanching and shocking spinach in cold water preserves its bright emerald color.'],
        substitutions: [{ original: 'Paneer', substitute: 'Tofu or boiled potatoes (Aloo Palak)', note: 'Equally delicious vegan alternative.' }],
        food_waste_note: 'Rescues fresh spinach bunches before leaves start wilting.',
      },
    });
  }

  // Ensure 3 distinct cards
  if (tailored.length < 3) {
    for (const fresh of FRESH_USER_RECOMMENDED_MEALS) {
      if (!tailored.some((t) => t.recipe.title === fresh.recipe.title)) {
        tailored.push(fresh);
      }
      if (tailored.length >= 3) break;
    }
  }

  return tailored.slice(0, 3);
}
