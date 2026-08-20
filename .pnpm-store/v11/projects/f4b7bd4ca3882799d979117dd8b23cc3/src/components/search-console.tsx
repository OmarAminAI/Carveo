"use client";

import { useId, useState } from "react";
import { ArrowRight, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const vehicleSuggestions = ["Toyota Land Cruiser", "Toyota RAV4", "Nissan Patrol", "Mercedes-Benz C 200", "BMW X5", "Porsche 911", "Ford F-150", "Volkswagen Golf", "Lexus LC 500"];

export function SearchConsole() {
  const [mode, setMode] = useState<"direct" | "assistant">("direct");
  const [query, setQuery] = useState("");
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const [activeSuggestion, setActiveSuggestion] = useState(0);
  const suggestionListId = useId();
  const matchingSuggestions = vehicleSuggestions.filter((suggestion) =>
    suggestion.toLowerCase().includes(query.toLowerCase()),
  );

  function chooseSuggestion(suggestion: string) {
    setQuery(suggestion);
    setSuggestionsOpen(false);
  }

  return (
    <section className="border border-white/25 bg-[rgba(11,11,12,0.92)] p-4 text-white md:p-6" aria-label="Vehicle search">
      <div className="mb-5 flex w-full border border-white/20 p-1 md:w-fit" role="group" aria-label="Search mode">
        <Button type="button" className="min-w-0 flex-1 px-1 text-[11px] sm:px-2 sm:text-sm" variant={mode === "direct" ? "signal" : "ghost"} size="sm" onClick={() => setMode("direct")}>Search inventory</Button>
        <Button type="button" className="min-w-0 flex-1 px-1 text-[11px] sm:px-2 sm:text-sm" variant={mode === "assistant" ? "signal" : "ghost"} size="sm" onClick={() => setMode("assistant")}>Describe what you need</Button>
      </div>
      {mode === "direct" ? (
        <form action="/en-ae/cars" className="grid gap-2 md:grid-cols-[minmax(0,1fr)_180px_56px]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-4 top-7 z-10 size-5 -translate-y-1/2 text-steel" aria-hidden="true" />
            <input
              name="q"
              role="combobox"
              aria-label="Make or model"
              aria-autocomplete="list"
              aria-expanded={suggestionsOpen}
              aria-controls={suggestionListId}
              aria-activedescendant={suggestionsOpen && matchingSuggestions.length ? `${suggestionListId}-${activeSuggestion}` : undefined}
              autoComplete="off"
              value={query}
              placeholder="Make, model or keyword"
              className="h-14 w-full border border-white/25 bg-white px-12 text-obsidian outline-none focus:border-signal"
              onFocus={() => setSuggestionsOpen(true)}
              onBlur={() => setSuggestionsOpen(false)}
              onChange={(event) => {
                setQuery(event.target.value);
                setActiveSuggestion(0);
                setSuggestionsOpen(true);
              }}
              onKeyDown={(event) => {
                if (event.key === "Escape") setSuggestionsOpen(false);
                if (event.key === "ArrowDown" && matchingSuggestions.length) {
                  event.preventDefault();
                  setSuggestionsOpen(true);
                  setActiveSuggestion((current) => (current + 1) % matchingSuggestions.length);
                }
                if (event.key === "ArrowUp" && matchingSuggestions.length) {
                  event.preventDefault();
                  setSuggestionsOpen(true);
                  setActiveSuggestion((current) => (current - 1 + matchingSuggestions.length) % matchingSuggestions.length);
                }
                if (event.key === "Enter" && suggestionsOpen && matchingSuggestions.length) {
                  event.preventDefault();
                  chooseSuggestion(matchingSuggestions[activeSuggestion]);
                }
              }}
            />
            {suggestionsOpen ? (
              <div id={suggestionListId} role="listbox" className="absolute inset-x-0 top-[calc(100%+4px)] z-[70] max-h-64 overflow-y-auto border border-border bg-white p-1 text-obsidian">
                {matchingSuggestions.length ? matchingSuggestions.map((suggestion, index) => (
                  <div
                    id={`${suggestionListId}-${index}`}
                    key={suggestion}
                    role="option"
                    aria-selected={index === activeSuggestion}
                    className="cursor-default px-3 py-2 text-sm aria-selected:bg-signal"
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={() => chooseSuggestion(suggestion)}
                  >
                    {suggestion}
                  </div>
                )) : <p className="px-3 py-3 text-sm text-muted-foreground">No matching fixtures</p>}
              </div>
            ) : null}
          </div>
          <label>
            <span className="sr-only">Maximum budget</span>
            <select name="priceMax" aria-label="Maximum budget" className="h-14 w-full border border-white/25 bg-white px-4 text-obsidian outline-none focus:border-signal" defaultValue="">
              <option value="">Any budget</option><option value="100000">Under AED 100k</option><option value="200000">Under AED 200k</option><option value="300000">Under AED 300k</option>
            </select>
          </label>
          <Button variant="signal" className="h-14 px-0" aria-label="Search cars"><ArrowRight className="size-5" /></Button>
        </form>
      ) : (
        <form action="/en-ae/find" className="grid gap-2 md:grid-cols-[minmax(0,1fr)_auto]">
          <label className="relative block">
            <span className="sr-only">Describe your ideal car</span>
            <Sparkles className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-steel" aria-hidden="true" />
            <input name="prompt" aria-label="Describe your ideal car" placeholder="A reliable GCC SUV under AED 180k for a family of five" className="h-14 w-full border border-white/25 bg-white px-12 text-obsidian outline-none focus:border-signal" />
          </label>
          <Button variant="signal" className="h-14" type="submit">Start AI search <ArrowRight className="size-4" /></Button>
        </form>
      )}
    </section>
  );
}
