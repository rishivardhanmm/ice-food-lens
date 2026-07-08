import { AnalyzeFoodResponse } from "@/lib/api";

export default function NutritionSummary({ totals }: { totals: AnalyzeFoodResponse["totals"] }) {
  const cards = [
    { label: "Calories", value: `${Math.round(totals.calories_kcal)} kcal` },
    { label: "Protein", value: `${totals.protein_g.toFixed(1)} g` },
    { label: "Carbs", value: `${totals.carbs_g.toFixed(1)} g` },
    { label: "Fat", value: `${totals.fat_g.toFixed(1)} g` },
    { label: "Fibre", value: `${totals.fibre_g.toFixed(1)} g` },
    { label: "Sugar", value: `${totals.sugar_g.toFixed(1)} g` },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-6">
      {cards.map((c) => (
        <div key={c.label} className="rounded-lg border bg-white p-4 text-center shadow-sm">
          <div className="text-xs uppercase tracking-wide text-slate-500">{c.label}</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
