"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/api";

interface EvalSummary {
  total_predictions: number;
  predictions_by_model: Record<string, number>;
  avg_confidence: number | null;
  avg_confidence_by_category: Record<string, number>;
  training_examples_pending_review: number;
  training_examples_reviewed: number;
  note: string;
}

export default function EvaluationPage() {
  const [summary, setSummary] = useState<EvalSummary | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/evaluation/summary`)
      .then((r) => r.json())
      .then(setSummary)
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Evaluation Dashboard</h1>
        <p className="mt-1 text-slate-600">
          OpenAI vs internal model comparison, confidence calibration, and review queue.
        </p>
      </div>

      {!summary && <p className="text-sm text-slate-500">Loading…</p>}

      {summary && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Total predictions" value={summary.total_predictions} />
            <Stat label="Avg confidence" value={summary.avg_confidence ?? "—"} />
            <Stat label="Pending review" value={summary.training_examples_pending_review} />
            <Stat label="Reviewed" value={summary.training_examples_reviewed} />
          </div>

          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <h2 className="font-semibold">Predictions by model</h2>
            <ul className="mt-2 text-sm text-slate-600">
              {Object.entries(summary.predictions_by_model).map(([model, count]) => (
                <li key={model}>{model}: {count}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <h2 className="font-semibold">Avg confidence by category</h2>
            <ul className="mt-2 text-sm text-slate-600">
              {Object.entries(summary.avg_confidence_by_category).map(([cat, conf]) => (
                <li key={cat}>{cat}: {conf}</li>
              ))}
            </ul>
          </div>

          <p className="text-xs text-slate-400">{summary.note}</p>
        </>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border bg-white p-4 text-center shadow-sm">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
