export interface WasteScoreResult {
  score: number;
  label: 'Outstanding' | 'Excellent' | 'Great Effort' | 'Moderate' | 'Basic';
  colorClass: string;
  badgeBgClass: string;
  usedCount: number;
  totalAvailableCount: number;
  explanation: string;
  environmentalTip: string;
}

export function calculateFoodWasteScore(
  usedAvailableCount: number,
  totalAvailableCount: number,
  recipeUtilizationPercentage: number
): WasteScoreResult {
  if (totalAvailableCount <= 0) {
    return {
      score: 50,
      label: 'Moderate',
      colorClass: 'text-amber-600',
      badgeBgClass: 'bg-amber-100 border-amber-300 text-amber-800',
      usedCount: 0,
      totalAvailableCount: 0,
      explanation: 'No fridge items were selected as inputs.',
      environmentalTip: 'Snap a picture of your fridge to start rescuing ingredients before they spoil.',
    };
  }

  // Combine count ratio and AI utilization rating
  const ratio = usedAvailableCount / totalAvailableCount;
  const rawScore = Math.round(ratio * 60 + (recipeUtilizationPercentage / 100) * 40);
  const score = Math.min(100, Math.max(10, rawScore));

  let label: WasteScoreResult['label'] = 'Moderate';
  let colorClass = 'text-amber-600';
  let badgeBgClass = 'bg-amber-100 border-amber-300 text-amber-800';
  let environmentalTip = 'Using ingredients before they reach end-of-life avoids household food loss.';

  if (score >= 90) {
    label = 'Outstanding';
    colorClass = 'text-emerald-600';
    badgeBgClass = 'bg-emerald-100 border-emerald-300 text-emerald-800';
    environmentalTip = 'Fantastic job! Utilizing over 85% of your available fridge stock prevents landfill methane emissions and saves money.';
  } else if (score >= 75) {
    label = 'Excellent';
    colorClass = 'text-green-600';
    badgeBgClass = 'bg-green-100 border-green-300 text-green-800';
    environmentalTip = 'Great food conservation! You are actively repurposing ingredients before their expiration window.';
  } else if (score >= 60) {
    label = 'Great Effort';
    colorClass = 'text-teal-600';
    badgeBgClass = 'bg-teal-100 border-teal-300 text-teal-800';
    environmentalTip = 'Solid choice. Consider pairing remaining unused items into a side salad or broth base.';
  } else if (score >= 40) {
    label = 'Moderate';
    colorClass = 'text-amber-600';
    badgeBgClass = 'bg-amber-100 border-amber-300 text-amber-800';
    environmentalTip = 'Try selecting the "Best Match" recipe card to use more of your existing items.';
  } else {
    label = 'Basic';
    colorClass = 'text-orange-600';
    badgeBgClass = 'bg-orange-100 border-orange-300 text-orange-800';
    environmentalTip = 'Most ingredients in this recipe require purchasing new items.';
  }

  return {
    score,
    label,
    colorClass,
    badgeBgClass,
    usedCount: usedAvailableCount,
    totalAvailableCount,
    explanation: `${usedAvailableCount} of ${totalAvailableCount} confirmed available ingredients utilized in this meal.`,
    environmentalTip,
  };
}
