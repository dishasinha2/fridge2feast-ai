import React from 'react';
import { Leaf, Award, CheckCircle2, ShieldCheck, Info } from 'lucide-react';
import { calculateFoodWasteScore } from '../utils/wasteScore';

interface WasteScoreBadgeProps {
  usedAvailableCount: number;
  totalAvailableCount: number;
  recipeUtilizationPercentage: number;
}

export const WasteScoreBadge: React.FC<WasteScoreBadgeProps> = ({
  usedAvailableCount,
  totalAvailableCount,
  recipeUtilizationPercentage,
}) => {
  const result = calculateFoodWasteScore(usedAvailableCount, totalAvailableCount, recipeUtilizationPercentage);

  return (
    <div className="bg-gradient-to-br from-emerald-900 to-teal-950 text-white rounded-3xl p-6 sm:p-8 border border-emerald-800/80 shadow-xl relative overflow-hidden space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
        <div className="space-y-2 max-w-lg">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
            <Leaf className="w-3.5 h-3.5 text-emerald-400" />
            <span>Sustainability Impact</span>
          </div>
          <h3 className="text-2xl font-black tracking-tight text-white">
            Food Waste Reduction Score
          </h3>
          <p className="text-stone-300 text-xs sm:text-sm leading-relaxed">
            {result.explanation}
          </p>
        </div>

        {/* Score Radial Badge */}
        <div className="flex items-center gap-4 bg-stone-900/80 p-4 rounded-2xl border border-emerald-500/30 backdrop-blur-md flex-shrink-0">
          <div className="relative w-16 h-16 flex items-center justify-center font-black text-2xl text-emerald-400">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-stone-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-emerald-400"
                strokeDasharray={`${result.score}, 100`}
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span className="absolute">{result.score}</span>
          </div>

          <div>
            <span className={`text-xs font-extrabold px-2.5 py-1 rounded-full border ${result.badgeBgClass}`}>
              {result.label}!
            </span>
            <p className="text-[11px] text-stone-400 mt-1 font-medium">Out of 100 max impact</p>
          </div>
        </div>
      </div>

      {/* Environmental Tip Note */}
      <div className="pt-4 border-t border-emerald-800/60 flex items-start gap-3 text-xs text-stone-300">
        <Info className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        <p className="italic">{result.environmentalTip}</p>
      </div>
    </div>
  );
};
