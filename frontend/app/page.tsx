"use client";

import { useState } from "react";
import { analyzeFood, AnalyzeFoodResponse } from "@/lib/api";
import Disclaimer from "@/components/Disclaimer";
import NutritionSummary from "@/components/NutritionSummary";
import FoodItemTable from "@/components/FoodItemTable";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const [train, setTrain] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeFoodResponse | null>(null);

  function handleFileChange(f: File | null) {
    setFile(f);
    setResult(null);
    setError(null);
    if (f) setPreview(URL.createObjectURL(f));
    else setPreview(null);
  }

  async function handleAnalyze() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeFood(file, { train, notes });
      setResult(res);
    } catch (e: any) {
      setError(e.message ?? "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Upload a food photo</h1>
        <p className="mt-1 text-slate-600">Get an AI-estimated nutrition breakdown.</p>
      </div>

      <Disclaimer />

      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row">
          <div className="flex-1">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-brand-700 hover:file:bg-brand-100"
            />
            {preview && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={preview} alt="preview" className="mt-4 max-h-72 rounded-md border object-contain" />
            )}
            <textarea
              placeholder="Optional notes (e.g. 'homemade, no oil')"
              className="mt-4 w-full rounded-md border px-3 py-2 text-sm"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            <label className="mt-3 flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" checked={train} onChange={(e) => setTrain(e.target.checked)} />
              Save this example for model training (pending review)
            </label>
            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="mt-4 rounded-md bg-brand-600 px-4 py-2 font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {loading ? "Analysing..." : "Analyse food"}
            </button>
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Results</h2>
            <span className="text-xs text-slate-500">
              model: {result.model_used} · request: {result.request_id.slice(0, 8)}
            </span>
          </div>

          <NutritionSummary totals={result.totals} />

          <FoodItemTable items={result.items} predictionItemIds={result.prediction_item_ids} />

          {result.accuracy_warnings.length > 0 && (
            <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              <div className="font-medium">Assumptions & warnings</div>
              <ul className="mt-1 list-disc pl-5">
                {result.accuracy_warnings.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          )}

          {result.improvement_questions.length > 0 && (
            <div className="rounded-md border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
              <div className="font-medium">To improve accuracy, tell us:</div>
              <ul className="mt-1 list-disc pl-5">
                {result.improvement_questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
