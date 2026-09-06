"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useTransition, type AnchorHTMLAttributes, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { LoaderCircle } from "lucide-react";
import type { ListingQuery } from "@/domain/schemas";
import { FilterFields } from "./filter-fields";

const NavigationContext = createContext<{ pending: boolean; navigate: (params: URLSearchParams) => void; registerCancellation: (cancel: () => void) => () => void } | null>(null);
export function BrowseNavigation({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const cancellations = useRef(new Set<() => void>());
  const navigating = useRef(false);
  const registerCancellation = useCallback((cancel: () => void) => {
    cancellations.current.add(cancel);
    return () => { cancellations.current.delete(cancel); };
  }, []);
  useEffect(() => { if (!pending) navigating.current = false; }, [pending]);
  return <NavigationContext.Provider value={{ pending, registerCancellation, navigate: (params) => {
    if (navigating.current) return;
    navigating.current = true;
    cancellations.current.forEach((cancel) => cancel());
    startTransition(() => router.replace(`/en-ae/cars?${params}`, { scroll: false }));
  } }}>{children}</NavigationContext.Provider>;
}
function useBrowseNavigation() {
  const context = useContext(NavigationContext);
  if (!context) throw new Error("Browse controls require BrowseNavigation");
  return context;
}
export function BrowseResults({ children, summary }: { children: ReactNode; summary: string }) {
  const { pending } = useBrowseNavigation();
  return <section aria-label="Car results" aria-busy={pending} className="min-w-0">
    <p role="status" aria-live="polite" className="mb-4 flex min-h-6 items-center gap-2 text-sm text-muted-foreground">{pending ? <><LoaderCircle className="size-4 animate-spin motion-reduce:animate-none" />Updating cars…</> : summary}</p>
    <div inert={pending} className={`transition-opacity duration-150 motion-reduce:transition-none ${pending ? "pointer-events-none opacity-45" : ""}`}>{children}</div>
  </section>;
}
const filterKeys = ["q", "make", "model", "bodyType", "city", "specifications", "sellerType", "yearMin", "yearMax", "priceMin", "priceMax", "mileageMax", "evidence"];
export function FilterForm({ query, currentParams, mobile = false, onApplied }: { query: ListingQuery; currentParams: string; mobile?: boolean; onApplied?: () => void }) {
  const { pending, navigate, registerCancellation } = useBrowseNavigation();
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const resetDraft = useRef(false);
  const clearTimer = useCallback(() => { if (timer.current) clearTimeout(timer.current); timer.current = null; }, []);
  useEffect(() => registerCancellation(clearTimer), [registerCancellation, clearTimer]);
  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, [currentParams]);
  useEffect(() => { if (pending && timer.current) clearTimeout(timer.current); }, [pending]);
  function apply(form: HTMLFormElement) {
    clearTimer();
    if (!form.reportValidity()) return;
    const params = new URLSearchParams(currentParams);
    if (resetDraft.current) filterKeys.forEach((key) => params.delete(key));
    // Only replace rendered fields: model and other URL-only criteria survive.
    const inputs = Array.from(form.elements).filter((element): element is HTMLInputElement => element instanceof HTMLInputElement && !!element.name);
    for (const input of inputs) {
      if (input.type === "checkbox") params.delete(input.name, input.value);
      else params.delete(input.name);
    }
    for (const [name, value] of new FormData(form)) if (typeof value === "string" && value.trim()) params.append(name, value.trim());
    params.delete("page");
    navigate(params);
    onApplied?.();
  }
  return <form key={currentParams} onSubmit={(event) => { event.preventDefault(); apply(event.currentTarget); }} onChange={(event) => {
    if (mobile) return;
    clearTimer();
    const form = event.currentTarget;
    if (event.target instanceof HTMLInputElement && event.target.type !== "checkbox") timer.current = setTimeout(() => apply(form), 350);
    else apply(form);
  }}>
    <fieldset disabled={pending} className="min-w-0">
      <FilterFields query={query} />
      {mobile && <button type="submit" className="mt-6 flex h-12 w-full items-center justify-center rounded-lg bg-signal text-sm font-semibold text-obsidian">Show results</button>}
      <button type="button" className="mt-3 min-h-11 w-full rounded-lg text-sm font-medium underline underline-offset-4 hover:bg-marble" onClick={(event) => {
        clearTimer();
        const params = new URLSearchParams(currentParams);
        filterKeys.forEach((key) => params.delete(key)); params.delete("page");
        if (mobile) {
          resetDraft.current = true;
          const form = event.currentTarget.form;
          form?.querySelectorAll("input").forEach((input) => { if (input.type === "checkbox") input.checked = false; else input.value = ""; });
        } else navigate(params);
      }}>Reset filters</button>
    </fieldset>
  </form>;
}
export function BrowseSort({ sort, currentParams }: { sort: ListingQuery["sort"]; currentParams: string }) {
  const { pending, navigate } = useBrowseNavigation();
  return <label className="flex min-w-0 items-center gap-2 text-sm"><span className="shrink-0 text-muted-foreground">Sort by</span><select aria-label="Sort" value={sort} disabled={pending} onChange={(event) => { const params = new URLSearchParams(currentParams); params.set("sort", event.target.value); params.delete("page"); navigate(params); }} className="h-11 min-w-0 flex-1 rounded-lg border border-border bg-white px-2 text-sm font-medium sm:px-3"><option value="best-match">Best match</option><option value="best-deal">Best deal</option><option value="newest">Newest</option><option value="lowest-price">Lowest price</option><option value="lowest-mileage">Lowest mileage</option></select></label>;
}



export function BrowseLink({ params, children, ...props }: Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "href" | "onClick"> & { params: string }) {
  const { pending, navigate } = useBrowseNavigation();
  return <a {...props} href={pending ? undefined : `/en-ae/cars?${params}`} aria-disabled={pending || undefined} tabIndex={pending ? -1 : undefined} onClick={(event) => {
    if (pending) { event.preventDefault(); return; }
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate(new URLSearchParams(params));
  }}>{children}</a>;
}
