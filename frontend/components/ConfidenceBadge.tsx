export default function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round((confidence ?? 0) * 100);
  const color =
    pct >= 70 ? "bg-green-100 text-green-800" : pct >= 40 ? "bg-amber-100 text-amber-800" : "bg-red-100 text-red-800";
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {pct}% confidence
    </span>
  );
}
