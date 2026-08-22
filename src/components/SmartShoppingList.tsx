import React, { useState } from 'react';
import { ShoppingCart, Download, FileText, CheckSquare, Square } from 'lucide-react';
import { MissingIngredient } from '../types';
import { exportShoppingListAsCSV, exportShoppingListAsTXT, exportShoppingListAsMD } from '../utils/export';

interface SmartShoppingListProps {
  missingIngredients: MissingIngredient[];
  recipeTitle: string;
}

export const SmartShoppingList: React.FC<SmartShoppingListProps> = ({ missingIngredients, recipeTitle }) => {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  const toggleCheck = (index: number) => {
    setCheckedItems((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const totalCost = missingIngredients.reduce((sum, item) => sum + item.estimated_price_inr, 0);

  if (missingIngredients.length === 0) {
    return (
      <div className="bg-emerald-950/60 border border-emerald-500/30 rounded-3xl p-6 text-emerald-300 text-center space-y-2">
        <ShoppingCart className="w-8 h-8 text-emerald-400 mx-auto" />
        <h3 className="font-extrabold text-lg">No Missing Ingredients!</h3>
        <p className="text-xs text-emerald-400/80">
          You have 100% of the required ingredients in your fridge! You're ready to start cooking immediately.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-8 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-emerald-400" />
            <h3 className="text-xl font-black text-white">🛒 Smart Shopping List</h3>
          </div>
          <p className="text-slate-400 text-xs">
            Missing items to purchase for "{recipeTitle}"
          </p>
        </div>

        {/* Download Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => exportShoppingListAsCSV(missingIngredients, recipeTitle)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl border border-slate-700 flex items-center gap-1 transition-colors"
            title="Download CSV"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>CSV</span>
          </button>

          <button
            onClick={() => exportShoppingListAsTXT(missingIngredients, recipeTitle)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl border border-slate-700 flex items-center gap-1 transition-colors"
            title="Download TXT"
          >
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span>TXT</span>
          </button>

          <button
            onClick={() => exportShoppingListAsMD(missingIngredients, recipeTitle)}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-extrabold rounded-xl flex items-center gap-1 transition-colors shadow-sm"
            title="Download Markdown"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Markdown</span>
          </button>
        </div>
      </div>

      {/* ITEMS LIST */}
      <div className="divide-y divide-slate-800">
        {missingIngredients.map((item, idx) => {
          const isDone = !!checkedItems[idx];
          return (
            <div
              key={idx}
              onClick={() => toggleCheck(idx)}
              className={`py-3 flex items-center justify-between cursor-pointer group transition-colors px-2 rounded-xl ${
                isDone ? 'bg-slate-800/40 opacity-50 line-through' : 'hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                {isDone ? (
                  <CheckSquare className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                ) : (
                  <Square className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 flex-shrink-0" />
                )}
                <div>
                  <span className="font-extrabold text-white text-sm">{item.name}</span>
                  <span className="text-slate-400 text-xs ml-2">({item.estimated_quantity})</span>
                </div>
              </div>

              <span className="font-black text-emerald-400 text-xs bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
                ~ ₹{item.estimated_price_inr}
              </span>
            </div>
          );
        })}
      </div>

      {/* TOTAL COST BANNER */}
      <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between text-sm">
        <span className="font-bold text-slate-300 text-xs">Estimated Additional Shopping Cost:</span>
        <span className="font-black text-emerald-400 text-base">₹{totalCost}</span>
      </div>
    </div>
  );
};
