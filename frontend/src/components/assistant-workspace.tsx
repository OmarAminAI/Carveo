"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Route } from "next";
import { ArrowRight, RotateCcw, Send, Sparkles } from "lucide-react";
import { interpretFixturePrompt } from "@/domain/assistant";
import type { AnonymousConversation, AssistantTurn, SearchIntent } from "@/domain/schemas";
import { Bubble, Marker, Message, MessageScroller } from "@/components/ui/message";
import { Button, buttonVariants } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useProfile } from "@/profile/profile-provider";

const newId = () => crypto.randomUUID();

function intentHref(intent: SearchIntent): Route {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(intent)) {
    if (key === "conditionPreferences") continue;
    if (Array.isArray(value)) value.forEach((item) => params.append(key, String(item)));
    else if (value !== undefined) params.set(key, String(value));
  }
  return `/en-ae/cars?${params}` as Route;
}

export function AssistantWorkspace({ initialPrompt = "" }: { initialPrompt?: string }) {
  const { saveAssistantConversation, archiveAssistantConversation } = useProfile();
  const first = useMemo(() => interpretFixturePrompt(initialPrompt), [initialPrompt]);
  const [intent, setIntent] = useState<SearchIntent>(first.intent);
  const [clientId, setClientId] = useState(newId);
  const [createdAt, setCreatedAt] = useState(() => new Date().toISOString());
  const [messages, setMessages] = useState<AssistantTurn[]>(() => initialPrompt ? [
    { id: newId(), role: "buyer", content: initialPrompt },
    { id: newId(), role: "assistant", content: `I interpreted ${Object.keys(first.intent).length} requirement groups. Review them before searching.` },
  ] : [{ id: newId(), role: "assistant", content: "Tell me what matters: vehicle type, budget, year, location, and any source-stated condition evidence you want to see." }]);
  const [draft, setDraft] = useState("");
  const update = (key: keyof SearchIntent, value: string | number | string[] | undefined) => setIntent((current) => ({ ...current, [key]: value || undefined }));
  const send = () => {
    if (!draft.trim()) return;
    const parsed = interpretFixturePrompt(draft);
    const nextIntent = { ...intent, ...parsed.intent };
    const nextMessages: AssistantTurn[] = [
      ...messages,
      { id: newId(), role: "buyer", content: draft },
      { id: newId(), role: "assistant", content: parsed.summary },
    ];
    setIntent(nextIntent);
    setMessages(nextMessages);
    const conversation: AnonymousConversation = {
      clientId,
      title: draft.slice(0, 160),
      status: "active",
      interpretedIntent: nextIntent,
      createdAt,
      updatedAt: new Date().toISOString(),
      turns: nextMessages,
    };
    void saveAssistantConversation(conversation);
    setDraft("");
  };
  const startOver = () => {
    archiveAssistantConversation(clientId);
    setClientId(newId());
    setCreatedAt(new Date().toISOString());
    setIntent({});
    setMessages([{ id: newId(), role: "assistant", content: "Let’s start again. What kind of vehicle do you need?" }]);
  };
  const requirements = Object.entries(intent).filter(([, value]) => value !== undefined && (!Array.isArray(value) || value.length));
  return <div className="grid min-h-[calc(100svh-64px)] bg-marble lg:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
    <section className="flex min-h-[640px] flex-col border-r border-border bg-white">
      <div className="border-b border-border p-5 md:p-8"><div className="flex items-center gap-2 text-xs font-semibold uppercase text-muted-foreground"><Sparkles className="size-4 text-signal" />Fixture interpreter</div><h1 className="font-display mt-2 text-4xl font-semibold uppercase">Describe your next car</h1><p className="mt-2 text-sm text-muted-foreground">Deterministic local parsing only. No remote AI service is contacted.</p></div>
      <MessageScroller className="flex-1 space-y-4 p-5 md:p-8">{messages.map((message) => <Message key={message.id} className={message.role === "buyer" ? "justify-end" : "justify-start"}><Bubble className={message.role === "buyer" ? "border-obsidian bg-obsidian text-white" : "border-border bg-marble"}><Marker>{message.role === "buyer" ? "You" : "Carveo"}</Marker>{message.content}</Bubble></Message>)}</MessageScroller>
      <div className="border-t border-border p-4 md:p-6"><div className="flex gap-2"><textarea aria-label="Add requirements" value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); } }} placeholder="Add or change a requirement" className="min-h-12 flex-1 resize-none border border-input p-3 text-sm outline-none focus:border-obsidian" /><Button type="button" size="icon" className="h-12" aria-label="Send requirement" onClick={send}><Send className="size-4" /></Button></div></div>
    </section>
    <aside className="p-5 md:p-8"><div className="sticky top-24"><p className="text-xs font-semibold uppercase text-muted-foreground">Interpreted requirements</p><h2 className="font-display mt-2 text-3xl font-semibold uppercase">Your search brief</h2><div className="mt-5 flex flex-wrap gap-2">{requirements.map(([key, value]) => <Badge key={key} className={key === "conditionPreferences" ? "border-steel text-muted-foreground" : "border-obsidian"}>{key.replace(/([A-Z])/g, " $1")}: {Array.isArray(value) ? value.join(", ") : String(value)}</Badge>)}</div>
      <div className="mt-8 grid gap-4 border-y border-border py-6">
        <label className="grid gap-2 text-xs font-semibold uppercase">Make<input value={intent.make?.[0] ?? ""} onChange={(event) => update("make", event.target.value ? [event.target.value] : [])} className="h-11 border border-input bg-white px-3 text-sm font-normal normal-case" /></label>
        <label className="grid gap-2 text-xs font-semibold uppercase">Body type<select value={intent.bodyType?.[0] ?? ""} onChange={(event) => update("bodyType", event.target.value ? [event.target.value] : [])} className="h-11 border border-input bg-white px-3 text-sm font-normal normal-case"><option value="">Any</option>{["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"].map((value) => <option key={value}>{value}</option>)}</select></label>
        <div className="grid grid-cols-2 gap-3"><label className="grid gap-2 text-xs font-semibold uppercase">Year from<input aria-label="Minimum year" type="number" value={intent.yearMin ?? ""} onChange={(event) => update("yearMin", Number(event.target.value) || undefined)} className="h-11 min-w-0 border border-input bg-white px-3 text-sm font-normal" /></label><label className="grid gap-2 text-xs font-semibold uppercase">Budget up to<input aria-label="Maximum budget" type="number" value={intent.priceMax ?? ""} onChange={(event) => update("priceMax", Number(event.target.value) || undefined)} className="h-11 min-w-0 border border-input bg-white px-3 text-sm font-normal" /></label></div>
      </div>
      <div className="mt-6 flex gap-2"><Link href={intentHref(intent)} className={cn(buttonVariants({ variant: "signal" }), "flex-1")}>Search now <ArrowRight className="size-4" /></Link><Button type="button" variant="outline" size="icon" aria-label="Start over" onClick={startOver}><RotateCcw className="size-4" /></Button></div>
      <p className="mt-4 text-xs leading-relaxed text-muted-foreground">Condition phrases are preferences until a source states evidence. Carveo does not inspect vehicles.</p>
    </div></aside>
  </div>;
}
