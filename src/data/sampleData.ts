import { DetectedIngredient } from '../types';

export interface PresetFridge {
  id: string;
  title: string;
  description: string;
  badge: string;
  imageUrl: string;
  sampleIngredients: DetectedIngredient[];
}

// Crisp, lightweight data-URL food photo presets for instant capstone testing
export const SAMPLE_FRIDGE_PRESETS: PresetFridge[] = [
  {
    id: 'veggie-drawer',
    title: 'Veggie Drawer & Pantry Essentials',
    description: 'Fresh vegetables, eggs, cottage cheese (paneer), bell peppers, and herbs.',
    badge: 'Popular',
    imageUrl: 'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=800&q=80',
    sampleIngredients: [
      { id: '1', name: 'Tomatoes', category: 'Vegetable', estimated_quantity: '4 medium', confidence: 0.98, confidence_label: 'High', included: true },
      { id: '2', name: 'Bell Peppers (Capsicum)', category: 'Vegetable', estimated_quantity: '2 green & red', confidence: 0.95, confidence_label: 'High', included: true },
      { id: '3', name: 'Paneer (Cottage Cheese)', category: 'Dairy', estimated_quantity: '200g block', confidence: 0.92, confidence_label: 'High', included: true },
      { id: '4', name: 'Spinach (Palak)', category: 'Vegetable', estimated_quantity: '1 fresh bunch', confidence: 0.90, confidence_label: 'High', included: true },
      { id: '5', name: 'Eggs', category: 'Dairy', estimated_quantity: '6 eggs', confidence: 0.96, confidence_label: 'High', included: true },
      { id: '6', name: 'Onions', category: 'Vegetable', estimated_quantity: '3 large', confidence: 0.97, confidence_label: 'High', included: true },
      { id: '7', name: 'Plain Yogurt (Dahi)', category: 'Dairy', estimated_quantity: '1 tub (400g)', confidence: 0.88, confidence_label: 'High', included: true },
      { id: '8', name: 'Garlic & Ginger paste', category: 'Pantry/Spice', estimated_quantity: 'Half jar', confidence: 0.85, confidence_label: 'High', included: true },
    ],
  },
  {
    id: 'pantry-basics',
    title: 'Quick Snack & Italian Pantry',
    description: 'Pasta, mozzarella, cherry tomatoes, garlic, mushrooms, and olive oil.',
    badge: 'Quick Prep',
    imageUrl: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80',
    sampleIngredients: [
      { id: '10', name: 'Penne Pasta', category: 'Grain/Bakery', estimated_quantity: '500g box', confidence: 0.99, confidence_label: 'High', included: true },
      { id: '11', name: 'Cherry Tomatoes', category: 'Vegetable', estimated_quantity: '1 punnet (250g)', confidence: 0.95, confidence_label: 'High', included: true },
      { id: '12', name: 'Mozzarella Cheese', category: 'Dairy', estimated_quantity: '150g ball', confidence: 0.91, confidence_label: 'High', included: true },
      { id: '13', name: 'Button Mushrooms', category: 'Vegetable', estimated_quantity: '1 pack (200g)', confidence: 0.89, confidence_label: 'High', included: true },
      { id: '14', name: 'Fresh Basil', category: 'Vegetable', estimated_quantity: 'Small bunch', confidence: 0.86, confidence_label: 'High', included: true },
      { id: '15', name: 'Olive Oil', category: 'Pantry/Spice', estimated_quantity: '3/4 bottle', confidence: 0.94, confidence_label: 'High', included: true },
      { id: '16', name: 'Garlic Cloves', category: 'Vegetable', estimated_quantity: '1 whole bulb', confidence: 0.93, confidence_label: 'High', included: true },
    ],
  },
  {
    id: 'weekend-leftovers',
    title: 'Protein & Asian Leftovers',
    description: 'Tofu/Chicken, carrots, broccoli, soy sauce, rice, spring onion, and sesame.',
    badge: 'High Protein',
    imageUrl: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80',
    sampleIngredients: [
      { id: '20', name: 'Firm Tofu / Chicken Breast', category: 'Meat/Seafood', estimated_quantity: '300g pack', confidence: 0.94, confidence_label: 'High', included: true },
      { id: '21', name: 'Broccoli', category: 'Vegetable', estimated_quantity: '1 head', confidence: 0.96, confidence_label: 'High', included: true },
      { id: '22', name: 'Carrots', category: 'Vegetable', estimated_quantity: '3 medium', confidence: 0.95, confidence_label: 'High', included: true },
      { id: '23', name: 'Cooked Basmati Rice', category: 'Grain/Bakery', estimated_quantity: '2 cups left', confidence: 0.90, confidence_label: 'High', included: true },
      { id: '24', name: 'Soy Sauce', category: 'Condiment/Sauce', estimated_quantity: '1/2 bottle', confidence: 0.92, confidence_label: 'High', included: true },
      { id: '25', name: 'Spring Onions', category: 'Vegetable', estimated_quantity: '1 bundle', confidence: 0.88, confidence_label: 'High', included: true },
      { id: '26', name: 'Sesame Seeds & Oil', category: 'Pantry/Spice', estimated_quantity: 'Small jar', confidence: 0.84, confidence_label: 'High', included: true },
    ],
  },
];
