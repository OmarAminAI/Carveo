import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function MessageScroller({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div role="log" aria-live="polite" className={cn("overflow-y-auto overscroll-contain", className)} {...props} />; }
export function Message({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn("flex", className)} {...props} />; }
export function Bubble({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn("max-w-[85%] border p-4 text-sm leading-relaxed", className)} {...props} />; }
export function Marker({ children }: { children: React.ReactNode }) { return <span className="mb-1 block text-[11px] font-semibold uppercase text-muted-foreground">{children}</span>; }
