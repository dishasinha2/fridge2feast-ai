import React, { useState } from 'react';
import { Plus, Trash2, CheckCircle2, ShieldCheck, AlertTriangle, Filter, Search, ArrowRight } from 'lucide-react';
import { DetectedIngredient } from '../types';
import { VegetableDishKey } from './VegetableDishKey';

interface IngredientReviewProps {
  ingredients: DetectedIngredient[];
  uncertainItems?: string[];
  nonFoodItems?: string[];
  summary?: string;
  onUpdateIngredients: (updated: DetectedIngredient[]) => void;
  onConfirmAndContinue: () => void;
  onGoToScan?: () => void;
  onGoToRescue?: () => void;
}

const CATEGORY_OPTIONS = [
  'Vegetable',
  'Fruit',
  'Dairy',
  'Meat/Seafood',
  'Grain/Bakery',
  'Condiment/Sauce',
  'Beverage',
  'Pantry/Spice',
  'Other',
];

export const IngredientReview: React.FC<IngredientReviewProps> = ({
  ingredients = [],
  uncertainItems = [],
  nonFoodItems = [],
  summary,
  onUpdateIngredients,
  onConfirmAndContinue,
  onGoToScan,
  onGoToRescue,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [newIngredientName, setNewIngredientName] = useState<string>('');
  const [newCategory, setNewCategory] = useState<string>('Vegetable');
  const [newQuantity, setNewQuantity] = useState<string>('1 item');

  const safeIngredients = ingredients || [];

  const handleToggleInclude = (id: string) => {
    const updated = safeIngredients.map((item) =>
      item.id === id ? { ...item, included: !item.included } : item
    );
    onUpdateIngredients(updated);
  };

  const handleFieldChange = (id: string, field: keyof DetectedIngredient, value: any) => {
    const updated = safeIngredients.map((item) =>
      item.id === id ? { ...item, [field]: value } : item
    );
    onUpdateIngredients(updated);
  };

  const handleRemoveItem = (id: string) => {
    const updated = safeIngredients.filter((item) => item.id !== id);
    onUpdateIngredients(updated);
  };

  const handleAddManualIngredient = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newIngredientName.trim()) return;

    const newItem: DetectedIngredient = {
      id: `manual-${Date.now()}`,
      name: newIngredientName.trim(),
      category: newCategory,
      estimated_quantity: newQuantity.trim() || '1 item',
      confidence: 1.0,
      confidence_label: 'High',
      included: true,
    };

    onUpdateIngredients([...safeIngredients, newItem]);
    setNewIngredientName('');
    setNewQuantity('1 item');
  };

  const filteredIngredients = safeIngredients.filter((item) => {
    const matchesCat = filterCategory === 'All' || item.category === filterCategory;
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const confirmedCount = safeIngredients.filter((item) => item.included).length;
  const totalCount = safeIngredients.length;
  const categoriesCount = new Set(safeIngredients.map((i) => i.category)).size;

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-4 px-4 sm:px-6">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Kitchen Inventory</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            My Inventory
          </h1>
          <p className="text-slate-400 text-sm">
            Everything currently recorded in your kitchen. Adjust quantities or add pantry essentials.
          </p>
        </div>

        {/* TOP ACTIONS */}
        <div className="flex items-center gap-2">
          {onGoToRescue && (
            <button
              onClick={onGoToRescue}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
            >
              Rescue items
            </button>
          )}
          <button
            onClick={onConfirmAndContinue}
            id="top-generate-recipes-btn"
            className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-sm transition-colors"
          >
            Generate recipes from these items
          </button>
        </div>
      </div>

      {/* EMPTY INVENTORY STATE */}
      {totalCount === 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-10 text-center space-y-4">
          <div className="w-12 h-12 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h3 className="text-base font-bold text-white">Your inventory is currently empty</h3>
            <p className="text-xs text-slate-400">
              Scan your fridge or add ingredients manually to get customized recipe ideas.
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            {onGoToScan && (
              <button
                onClick={onGoToScan}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl"
              >
                Scan fridge
              </button>
            )}
          </div>
        </div>
      )}

      {/* METRICS SUMMARY */}
      {totalCount > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <p className="text-xs font-medium text-slate-400">Total Items</p>
            <p className="text-xl font-bold text-white mt-0.5">{totalCount}</p>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <p className="text-xs font-medium text-slate-400">Active for Cooking</p>
            <p className="text-xl font-bold text-emerald-400 mt-0.5">{confirmedCount}</p>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <p className="text-xs font-medium text-slate-400">Categories</p>
            <p className="text-xl font-bold text-slate-200 mt-0.5">{categoriesCount}</p>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <p className="text-xs font-medium text-slate-400">Freshness Status</p>
            <p className="text-xl font-bold text-emerald-400 mt-0.5">Tracked</p>
          </div>
        </div>
      )}

      {/* ADD MANUAL INGREDIENT FORM */}
      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-3">
        <h3 className="font-bold text-white text-sm">
          Add item manually
        </h3>

        <form onSubmit={handleAddManualIngredient} className="grid grid-cols-1 sm:grid-cols-12 gap-2.5">
          <div className="sm:col-span-5">
            <input
              type="text"
              placeholder="Ingredient name (e.g. Tomatoes, Eggs, Tofu)"
              value={newIngredientName}
              onChange={(e) => setNewIngredientName(e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-xs placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="sm:col-span-3">
            <select
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-xs focus:outline-none focus:border-emerald-500"
            >
              {CATEGORY_OPTIONS.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2">
            <input
              type="text"
              placeholder="Qty (e.g. 200g, 2 pcs)"
              value={newQuantity}
              onChange={(e) => setNewQuantity(e.target.value)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-xs focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="sm:col-span-2">
            <button
              type="submit"
              className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl transition-colors flex items-center justify-center gap-1"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          </div>
        </form>
      </div>

      {/* EDITABLE INVENTORY TABLE */}
      {totalCount > 0 && (
        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-white text-xs rounded-xl px-3 py-1.5 focus:outline-none focus:border-emerald-500"
              >
                <option value="All">All Categories ({ingredients.length})</option>
                {CATEGORY_OPTIONS.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search inventory..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white text-xs rounded-xl pl-8 pr-3 py-1.5 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          {/* INVENTORY TABLE */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="py-2.5 px-3 text-center">Use</th>
                  <th className="py-2.5 px-3">Ingredient</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Quantity</th>
                  <th className="py-2.5 px-3">Freshness Window</th>
                  <th className="py-2.5 px-3 text-right">Remove</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {filteredIngredients.length > 0 ? (
                  filteredIngredients.map((item) => {
                    const isPerishable = item.category === 'Vegetable' || item.category === 'Dairy' || item.category === 'Meat/Seafood';
                    return (
                      <tr key={item.id} className={`hover:bg-slate-800/40 transition-colors ${!item.included ? 'opacity-40' : ''}`}>
                        <td className="py-2.5 px-3 text-center">
                          <input
                            type="checkbox"
                            checked={item.included}
                            onChange={() => handleToggleInclude(item.id)}
                            className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 bg-slate-800 border-slate-700 cursor-pointer"
                          />
                        </td>
                        <td className="py-2.5 px-3">
                          <input
                            type="text"
                            value={item.name}
                            onChange={(e) => handleFieldChange(item.id, 'name', e.target.value)}
                            className="bg-transparent border-b border-transparent hover:border-slate-700 focus:border-emerald-500 text-white font-semibold focus:outline-none px-1 py-0.5 w-full"
                          />
                        </td>
                        <td className="py-2.5 px-3">
                          <select
                            value={item.category}
                            onChange={(e) => handleFieldChange(item.id, 'category', e.target.value)}
                            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-2 py-1 focus:outline-none"
                          >
                            {CATEGORY_OPTIONS.map((cat) => (
                              <option key={cat} value={cat}>{cat}</option>
                            ))}
                          </select>
                        </td>
                        <td className="py-2.5 px-3">
                          <input
                            type="text"
                            value={item.estimated_quantity}
                            onChange={(e) => handleFieldChange(item.id, 'estimated_quantity', e.target.value)}
                            className="bg-transparent border-b border-transparent hover:border-slate-700 focus:border-emerald-500 text-slate-300 focus:outline-none px-1 py-0.5 w-full"
                          />
                        </td>
                        <td className="py-2.5 px-3">
                          {isPerishable ? (
                            <span className="text-[11px] font-medium text-amber-400">
                              Best in 1–2 days
                            </span>
                          ) : (
                            <span className="text-[11px] text-slate-400">
                              Stable pantry item
                            </span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <button
                            onClick={() => handleRemoveItem(item.id)}
                            className="p-1.5 text-slate-400 hover:text-rose-400 transition-colors"
                            title="Remove ingredient"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-slate-400 text-xs">
                      No ingredients match your current filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* ACTION BAR */}
          <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-xs text-slate-400 font-medium">
              {confirmedCount} of {totalCount} ingredients selected
            </p>

            <button
              onClick={onConfirmAndContinue}
              id="confirm-inventory-btn"
              className="w-full sm:w-auto px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-sm transition-colors flex items-center justify-center gap-2"
            >
              <span>Generate recipes from these items</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* VEGETABLE-TO-FEAST KEY FOR DETECTED VEGETABLES */}
      <VegetableDishKey
        ingredients={safeIngredients}
        onGenerateRecipesWithKey={onConfirmAndContinue}
        onOpenRecipeStudio={onConfirmAndContinue}
      />
    </div>
  );
};
