"use client";

import { useState } from "react";
import { FoodItem } from "@/lib/api";
import ConfidenceBadge from "./ConfidenceBadge";
import CorrectionForm from "./CorrectionForm";

export default function FoodItemTable({
  items,
  predictionItemIds,
}: {
  items: FoodItem[];
  predictionItemIds: string[];
}) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  return (
    <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-2 text-left font-medium text-slate-600">Item</th>
            <th className="px-4 py-2 text-left font-medium text-slate-600">Quantity</th>
            <th className="px-4 py-2 text-left font-medium text-slate-600">Calories</th>
            <th className="px-4 py-2 text-left font-medium text-slate-600">Protein</th>
            <th className="px-4 py-2 text-left font-medium text-slate-600">Carbs</th>
            <th className="px-4 py-2 text-left font-medium text-slate-600">Fat</th>
            <th className="px-4 py-2 text-left font-medium text-slate-600">Confidence</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((item, i) => (
            <>
              <tr key={i} className="hover:bg-slate-50">
                <td className="px-4 py-2">
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs text-slate-500">{item.category}</div>
                </td>
                <td className="px-4 py-2">
                  {item.estimated_quantity.value} {item.estimated_quantity.unit}
                </td>
                <td className="px-4 py-2">{Math.round(item.calories_kcal)} kcal</td>
                <td className="px-4 py-2">{item.macros.protein_g.toFixed(1)} g</td>
                <td className="px-4 py-2">{item.macros.carbs_g.toFixed(1)} g</td>
                <td className="px-4 py-2">{item.macros.fat_g.toFixed(1)} g</td>
                <td className="px-4 py-2"><ConfidenceBadge confidence={item.confidence} /></td>
                <td className="px-4 py-2">
                  <button
                    className="text-brand-600 hover:underline"
                    onClick={() => setEditingIndex(editingIndex === i ? null : i)}
                  >
                    {editingIndex === i ? "Close" : "Correct"}
                  </button>
                </td>
              </tr>
              {editingIndex === i && (
                <tr>
                  <td colSpan={8} className="px-4 pb-3">
                    <CorrectionForm
                      item={item}
                      predictionItemId={predictionItemIds[i]}
                      onSaved={() => setEditingIndex(null)}
                    />
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}
