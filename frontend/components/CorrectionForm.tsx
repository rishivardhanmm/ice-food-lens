"use client";

import { useState } from "react";
import { FoodItem, submitCorrection } from "@/lib/api";

export default function CorrectionForm({
  item,
  predictionItemId,
  onSaved,
}: {
  item: FoodItem;
  predictionItemId: string;
  onSaved: () => void;
}) {
  const [name, setName] = useState(item.name);
  const [quantity, setQuantity] = useState(item.estimated_quantity.value);
  const [calories, setCalories] = useState(item.calories_kcal);
  const [protein, setProtein] = useState(item.macros.protein_g);
  const [carbs, setCarbs] = useState(item.macros.carbs_g);
  const [fat, setFat] = useState(item.macros.fat_g);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      await submitCorrection({
        prediction_item_id: predictionItemId,
        corrected_name: name,
        corrected_quantity_value: quantity,
        corrected_quantity_unit: item.estimated_quantity.unit,
        corrected_calories_kcal: calories,
        corrected_protein_g: protein,
        corrected_carbs_g: carbs,
        corrected_fat_g: fat,
        notes,
      });
      setSaved(true);
      onSaved();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mt-3 grid grid-cols-2 gap-2 rounded-md bg-slate-50 p-3 text-sm sm:grid-cols-3">
      <label className="flex flex-col gap-1">
        Name
        <input className="rounded border px-2 py-1" value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      <label className="flex flex-col gap-1">
        Quantity ({item.estimated_quantity.unit})
        <input type="number" className="rounded border px-2 py-1" value={quantity}
          onChange={(e) => setQuantity(Number(e.target.value))} />
      </label>
      <label className="flex flex-col gap-1">
        Calories
        <input type="number" className="rounded border px-2 py-1" value={calories}
          onChange={(e) => setCalories(Number(e.target.value))} />
      </label>
      <label className="flex flex-col gap-1">
        Protein (g)
        <input type="number" className="rounded border px-2 py-1" value={protein}
          onChange={(e) => setProtein(Number(e.target.value))} />
      </label>
      <label className="flex flex-col gap-1">
        Carbs (g)
        <input type="number" className="rounded border px-2 py-1" value={carbs}
          onChange={(e) => setCarbs(Number(e.target.value))} />
      </label>
      <label className="flex flex-col gap-1">
        Fat (g)
        <input type="number" className="rounded border px-2 py-1" value={fat}
          onChange={(e) => setFat(Number(e.target.value))} />
      </label>
      <label className="col-span-2 flex flex-col gap-1 sm:col-span-3">
        Notes
        <textarea className="rounded border px-2 py-1" value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      <div className="col-span-2 sm:col-span-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded-md bg-brand-600 px-3 py-1.5 text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : saved ? "Saved ✓" : "Save correction"}
        </button>
      </div>
    </div>
  );
}
