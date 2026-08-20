import { AlertTriangle, Check, HelpCircle } from "lucide-react";
import type { ConditionEvidence } from "@/domain/schemas";

const groups = [
  { kind: "positive" as const, title: "Source-stated positives", icon: Check },
  { kind: "warning" as const, title: "Warnings", icon: AlertTriangle },
  { kind: "unknown" as const, title: "Unknown", icon: HelpCircle },
];

export function ConditionEvidencePanel({ evidence }: { evidence: ConditionEvidence[] }) {
  return <div className="grid gap-4 lg:grid-cols-3">{groups.map(({ kind, title, icon: Icon }) => { const items = evidence.filter((item) => item.kind === kind); return <section key={kind} className="border border-border bg-white p-5"><Icon className={kind === "warning" ? "size-5 text-destructive" : kind === "positive" ? "size-5 text-[#18794e]" : "size-5 text-steel"} /><h3 className="mt-4 text-sm font-semibold">{title}</h3>{items.length ? <div className="mt-4 grid gap-3">{items.map((item) => <div key={`${item.label}-${item.detail}`}><p className="text-sm font-medium">{item.label}</p><p className="mt-1 text-xs leading-relaxed text-muted-foreground">{item.detail}</p></div>)}</div> : <p className="mt-4 text-xs text-muted-foreground">No source claim in this group.</p>}</section>; })}</div>;
}
