import type { DealPosition as DealPositionType } from "@/domain/schemas";

export function DealPosition({ position, compact = false }: { position?: DealPositionType | null; compact?: boolean }) {
  if (!position || position.label === "Limited data") return <span className="text-xs text-muted-foreground">Limited market data</span>;
  const positive = position.label === "Below typical";
  return (
    <div>
      <span className={positive ? "bg-signal px-2 py-1 text-xs font-bold text-obsidian" : "border border-border px-2 py-1 text-xs font-bold"}>{position.label}</span>
      {!compact && <p className="mt-2 text-xs text-muted-foreground">{position.sampleSize} comparable listings · typical AED {position.typicalPrice?.toLocaleString("en-AE")}</p>}
    </div>
  );
}
