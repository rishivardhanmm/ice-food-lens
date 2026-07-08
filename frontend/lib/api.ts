export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface FoodItem {
  name: string;
  category: string;
  estimated_quantity: { value: number; unit: string };
  calories_kcal: number;
  macros: {
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fibre_g: number;
    sugar_g: number;
  };
  micronutrients: Record<string, number | undefined>;
  confidence: number;
  reasoning_summary: string;
  assumptions: string[];
}

export interface AnalyzeFoodResponse {
  request_id: string;
  model_used: string;
  train: boolean;
  status: string;
  image_metadata: { filename: string; width: number; height: number };
  items: FoodItem[];
  totals: {
    calories_kcal: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fibre_g: number;
    sugar_g: number;
  };
  accuracy_warnings: string[];
  improvement_questions: string[];
  prediction_id: string;
  prediction_item_ids: string[];
}

export async function analyzeFood(
  file: File,
  opts: { train?: boolean; notes?: string; useInternalModel?: boolean; fallbackToOpenai?: boolean } = {}
): Promise<AnalyzeFoodResponse> {
  const form = new FormData();
  form.append("image", file);
  form.append("train", String(opts.train ?? false));
  form.append("source", "ui");
  if (opts.notes) form.append("notes", opts.notes);
  form.append("use_internal_model", String(opts.useInternalModel ?? false));
  form.append("fallback_to_openai", String(opts.fallbackToOpenai ?? true));

  const res = await fetch(`${API_BASE_URL}/api/analyze-food`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Analyze failed (${res.status}): ${text}`);
  }
  return res.json();
}

export async function submitCorrection(payload: {
  prediction_item_id: string;
  corrected_name?: string;
  corrected_quantity_value?: number;
  corrected_quantity_unit?: string;
  corrected_calories_kcal?: number;
  corrected_protein_g?: number;
  corrected_carbs_g?: number;
  corrected_fat_g?: number;
  notes?: string;
}) {
  const res = await fetch(`${API_BASE_URL}/api/corrections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Correction failed (${res.status})`);
  return res.json();
}
