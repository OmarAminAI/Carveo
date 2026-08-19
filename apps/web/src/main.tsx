import { useEffect, useMemo, useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";
import { createSession, getResults, type IntentState, type Match, sendMessage } from "./api";
import "./styles.css";

type Message = { role: "user" | "assistant"; content: string };
type WorkspaceView = "matches" | "compare";
type SortOrder = "score" | "price" | "mileage";

function formatIntent(intent: IntentState["intent"]): string[] {
  return [intent.market, intent.city, intent.make, ...intent.models, intent.year_min?.toString(), intent.budget_max ? `${intent.currency ?? "AED"} ${intent.budget_max.toLocaleString()} max` : undefined, intent.mileage_max_km ? `${intent.mileage_max_km.toLocaleString()} km max` : undefined, ...intent.colors, ...intent.specifications, ...intent.condition_preferences].filter((value): value is string => Boolean(value));
}

function matchSignal(match: Match): string {
  if (match.warnings.length) return "Needs review";
  if (match.score >= 80) return "Strong fit";
  return "Potential fit";
}

function ResultCard({ match, position }: { match: Match; position: number }) {
  const { listing } = match;
  const signals = [`${listing.year}`, `${listing.mileage_km.toLocaleString()} km`, listing.color ?? "Color pending", listing.seller_type];
  return <article className="result-card">
    <div className="result-card-topline"><p className="source-label">{String(position + 1).padStart(2, "0")} / {listing.source_name} / {listing.city}</p><span className={`fit-label ${match.warnings.length ? "review" : ""}`}>{matchSignal(match)}</span></div>
    <div className="result-heading"><div><h3>{listing.title}</h3><p className="result-meta">{signals.join("  /  ")}</p></div><div className="score-block"><strong>{Math.round(match.score)}</strong><span>fit score</span></div></div>
    <div className="result-summary"><p className="price">{listing.currency} {listing.price.toLocaleString()}</p><p className="spec-line">{listing.specifications.join(" / ") || "Specifications not listed"}{listing.warranty ? " / Warranty" : ""}</p></div>
    {match.reasons.length > 0 && <p className="reason">{match.reasons.join(". ")}</p>}
    {match.warnings.length > 0 && <div className="warning-list">{match.warnings.map((warning) => <p className="warning" key={warning}>{warning}</p>)}</div>}
    <div className="card-footer"><span>{listing.condition_signals[0] ?? "Condition details pending"}</span><a href={listing.source_url} target="_blank" rel="noreferrer">Open listing</a></div>
  </article>;
}

function ComparisonTable({ matches }: { matches: Match[] }) {
  return <div className="comparison-wrap"><div className="comparison-intro"><p className="panel-kicker">Side-by-side review</p><h3>Compare shortlisted options</h3></div><div className="comparison-scroll"><table><thead><tr><th>Vehicle</th><th>Fit</th><th>Price</th><th>Mileage</th><th>Specs</th><th>Condition</th><th>Source</th></tr></thead><tbody>{matches.map(({ listing, score }) => <tr key={listing.id}><td><strong>{listing.title}</strong><span>{listing.year} / {listing.city}</span></td><td><strong>{Math.round(score)}</strong><span>score</span></td><td>{listing.currency} {listing.price.toLocaleString()}</td><td>{listing.mileage_km.toLocaleString()} km</td><td>{listing.specifications.join(", ") || "Not listed"}</td><td>{listing.condition_signals.join(". ") || "Not listed"}</td><td><a href={listing.source_url} target="_blank" rel="noreferrer">Open</a></td></tr>)}</tbody></table></div></div>;
}

function App() {
  const [sessionId, setSessionId] = useState<string>();
  const [intentState, setIntentState] = useState<IntentState>();
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", content: "Tell me the car you are looking for and the details that matter most." }]);
  const [text, setText] = useState("");
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [view, setView] = useState<WorkspaceView>("matches");
  const [sortOrder, setSortOrder] = useState<SortOrder>("score");

  useEffect(() => { createSession().then((session) => { setSessionId(session.session_id); setIntentState(session.intent_state); }).catch(() => setError("Carveo is unavailable. Start the API and try again.")); }, []);
  const sortedMatches = useMemo(() => [...matches].sort((first, second) => sortOrder === "price" ? first.listing.price - second.listing.price : sortOrder === "mileage" ? first.listing.mileage_km - second.listing.mileage_km : second.score - first.score), [matches, sortOrder]);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!sessionId || !text.trim() || loading) return;
    const content = text.trim(); setText(""); setLoading(true); setError(undefined); setMessages((current) => [...current, { role: "user", content }]);
    try { const response = await sendMessage(sessionId, content); setIntentState(response.intent_state); setMessages((current) => [...current, response.message]); if (response.intent_state.ready) { const results = await getResults(sessionId); setMatches(results.matches); setView("matches"); } } catch { setError("Carveo could not process that message. Please try again."); } finally { setLoading(false); }
  }
  const brief = intentState ? formatIntent(intentState.intent) : [];
  return <main className="app-shell">
    <header className="topbar"><a className="brand" href="/" aria-label="Carveo home"><span className="brand-mark" aria-hidden="true">C</span><span>CARVEO</span></a><div className="topbar-status"><span className="status-dot" aria-hidden="true" />Buyer research workspace <span className="status-divider">/</span> UAE</div></header>
    <section className="workspace-heading"><div><p className="panel-kicker">Vehicle intelligence</p><h1>Search with more context.</h1></div><p>Describe the car, constraints, and trade-offs. Carveo turns the brief into a reviewable shortlist.</p></section>
    <section className="workspace">
      <aside className="brief-panel"><div className="panel-heading"><div><p className="panel-kicker">01 / Search brief</p><h2>Refine the request</h2></div><span className={`session-state ${sessionId ? "active" : ""}`}>{sessionId ? "Live" : "Connecting"}</span></div><div className="messages" aria-live="polite">{messages.map((message, index) => <p className={`message ${message.role}`} key={`${message.role}-${index}`}>{message.content}</p>)}</div><div className="brief-summary"><div className="brief-summary-title"><span>Captured criteria</span><span>{brief.length}</span></div>{brief.length ? <div className="intent-tags">{brief.map((tag, index) => <small key={`${tag}-${index}`}>{tag}</small>)}</div> : <p>Market, make, budget, and preferences will appear here as they are captured.</p>}</div><form onSubmit={submit} className="search-form"><label htmlFor="message">Add a detail</label><textarea id="message" value={text} onChange={(event) => setText(event.target.value)} placeholder="Example: 2023 Mercedes C-Class in UAE, under AED 180k, black, GCC specs, accident-free, under 50k km" /><div className="form-footer"><span>{loading ? "Reviewing request" : "One message at a time"}</span><button disabled={!sessionId || loading}>{loading ? "Working" : "Update brief"}</button></div></form>{error && <p className="error" role="alert">{error}</p>}</aside>
      <section className="results-panel"><div className="results-toolbar"><div><p className="panel-kicker">02 / Shortlist</p><h2>{matches.length ? `${matches.length} matches ready for review` : "Awaiting your search brief"}</h2></div>{matches.length > 0 && <div className="toolbar-actions"><div className="view-switch" aria-label="Results view"><button className={view === "matches" ? "selected" : ""} onClick={() => setView("matches")}>Matches</button><button className={view === "compare" ? "selected" : ""} onClick={() => setView("compare")}>Compare</button></div><label className="sort-control">Sort <select value={sortOrder} onChange={(event) => setSortOrder(event.target.value as SortOrder)}><option value="score">Best fit</option><option value="price">Lowest price</option><option value="mileage">Lowest mileage</option></select></label></div>}</div>{matches.length > 0 ? <><div className="results-context"><span className="ready-indicator"><i aria-hidden="true" />Search complete</span><span>Fixture catalogue / live source connection follows in Phase 4</span></div>{view === "matches" ? <div className="results-grid">{sortedMatches.map((match, index) => <ResultCard key={match.listing.id} match={match} position={index} />)}</div> : <ComparisonTable matches={sortedMatches} />}</> : <div className="empty-state"><span className="empty-index">02</span><div><h3>Your shortlist will appear here.</h3><p>Carveo needs a market, make, year, budget, and at least two preferences before it can build a useful comparison.</p></div></div>}</section>
    </section>
  </main>;
}

createRoot(document.getElementById("root")!).render(<App />);
