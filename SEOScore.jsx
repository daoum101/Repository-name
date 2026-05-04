import { Check, X } from "lucide-react";

export default function SEOScore({ data }) {
  if (!data) return null;
  const { score, checks } = data;
  const r = 44;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;
  const color = score >= 80 ? "hsl(142 70% 45%)" : score >= 60 ? "hsl(40 90% 55%)" : "hsl(0 80% 55%)";

  return (
    <div data-testid="seo-score" className="p-6 rounded-2xl border border-border bg-card">
      <div className="flex items-center gap-6">
        <div className="relative w-28 h-28 flex-shrink-0">
          <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
            <circle cx="50" cy="50" r={r} stroke="hsl(var(--muted))" strokeWidth="8" fill="none" />
            <circle
              cx="50" cy="50" r={r}
              stroke={color}
              strokeWidth="8"
              fill="none"
              strokeDasharray={c}
              strokeDashoffset={offset}
              strokeLinecap="round"
              style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.22, 1, 0.36, 1)" }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <span className="text-3xl font-medium" data-testid="seo-score-value">{score}</span>
            <span className="label-mono !text-[9px]">/ 100</span>
          </div>
        </div>
        <div>
          <div className="label-mono mb-1">Score SEO</div>
          <div className="text-xl font-medium leading-tight">
            {score >= 80 ? "Excellent" : score >= 60 ? "Correct" : "À améliorer"}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            {checks.filter((c) => c.passed).length} / {checks.length} critères validés
          </p>
        </div>
      </div>
      <ul className="mt-6 grid sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
        {checks.map((c) => (
          <li key={c.key} className="flex items-center gap-2" data-testid={`seo-check-${c.key}`}>
            {c.passed ? (
              <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
            ) : (
              <X className="w-4 h-4 text-destructive flex-shrink-0" />
            )}
            <span className={c.passed ? "" : "text-muted-foreground"}>{c.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
