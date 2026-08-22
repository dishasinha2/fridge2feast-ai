import React from 'react';
import { BarChart3, TrendingUp, DollarSign, Utensils, Leaf, Camera } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { SessionHistoryItem } from '../types';

interface AnalyticsDashboardProps {
  sessionHistory: SessionHistoryItem[];
  savedCount: number;
  onGoToScan: () => void;
}

const COLOR_PALETTE = ['#10b981', '#14b8a6', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899'];

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  sessionHistory = [],
  savedCount = 0,
  onGoToScan,
}) => {
  const safeHistory = sessionHistory || [];
  // Aggregate data
  const totalScans = safeHistory.length;
  const totalRecipesGenerated = safeHistory.reduce((sum, item) => sum + (item.recipes ? item.recipes.length : 0), 0);

  let totalUtilizationSum = 0;
  let totalUtilizationCount = 0;
  let totalIngredientsRescued = 0;

  const categoryCounts: Record<string, number> = {};
  const cuisineCounts: Record<string, number> = {};

  safeHistory.forEach((session) => {
    if (session && session.confirmedIngredients) {
      totalIngredientsRescued += session.confirmedIngredients.length;

      session.confirmedIngredients.forEach((ing) => {
        const cat = ing.category || 'Pantry/Spice';
        categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
      });
    }

    if (session && session.recipes) {
      session.recipes.forEach((recipe) => {
        totalUtilizationSum += recipe.ingredient_utilization_percentage || 0;
        totalUtilizationCount++;

        const cuisine = recipe.cuisine || 'Fusion';
        cuisineCounts[cuisine] = (cuisineCounts[cuisine] || 0) + 1;
      });
    }
  });

  const avgWasteScore = totalUtilizationCount > 0 ? Math.round(totalUtilizationSum / totalUtilizationCount) : 0;
  const estimatedMoneySaved = totalIngredientsRescued * 45; // ~₹45 saved per rescued ingredient

  const categoryChartData = Object.entries(categoryCounts).map(([name, value]) => ({ name, value }));
  const cuisineChartData = Object.entries(cuisineCounts).map(([name, value]) => ({ name, value }));

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-4 px-4 sm:px-6">
      {/* TITLE HEADER */}
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>Real-time Impact</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Sustainability & Waste Metrics
        </h1>
        <p className="text-slate-400 text-sm">
          Actual metrics calculated from your scanned ingredients and generated zero-waste recipes.
        </p>
      </div>

      {/* KPI METRICS CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-sm space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Utensils className="w-3.5 h-3.5 text-slate-400" />
            Total Recipes
          </span>
          <p className="text-2xl font-bold text-white">{totalRecipesGenerated || savedCount}</p>
        </div>

        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-sm space-y-1">
          <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
            <Leaf className="w-3.5 h-3.5 text-emerald-400" />
            Avg Waste Score
          </span>
          <p className="text-2xl font-bold text-emerald-400">
            {avgWasteScore > 0 ? `${avgWasteScore} / 100` : '—'}
          </p>
        </div>

        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-sm space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5 text-slate-400" />
            Rescued Items
          </span>
          <p className="text-2xl font-bold text-white">{totalIngredientsRescued}</p>
        </div>

        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-sm space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <DollarSign className="w-3.5 h-3.5 text-slate-400" />
            Est. Money Saved
          </span>
          <p className="text-2xl font-bold text-emerald-400">₹{estimatedMoneySaved}</p>
        </div>
      </div>

      {/* CHARTS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Category Distribution Chart */}
        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4">
          <h3 className="font-extrabold text-white text-base">
            Rescued Ingredients by Category
          </h3>

          {categoryChartData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData}>
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', color: '#fff', fontSize: '12px', border: '1px solid #334155' }}
                  />
                  <Bar dataKey="value" fill="#10b981" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400 text-xs space-y-3">
              <p>No category scans recorded in this session yet.</p>
              <button
                onClick={onGoToScan}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md inline-flex items-center gap-1.5"
              >
                <Camera className="w-3.5 h-3.5" />
                <span>Scan Fridge Now</span>
              </button>
            </div>
          )}
        </div>

        {/* Cuisine Preference Distribution */}
        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4">
          <h3 className="font-extrabold text-white text-base">
            Recipe Cuisine Distribution
          </h3>

          {cuisineChartData.length > 0 ? (
            <div className="h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={cuisineChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {cuisineChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLOR_PALETTE[index % COLOR_PALETTE.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', color: '#fff', fontSize: '12px', border: '1px solid #334155' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-xs text-slate-400 text-center py-16">
              Generate recipes to visualize cuisine breakdown.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
