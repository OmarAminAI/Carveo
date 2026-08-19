import { useEffect, useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";
import { createSession, getResults, type IntentState, type Match, sendMessage } from "./api";
import "./styles.css";

type Message = { role: "user" | "assistant"; content: string };

function formatIntent(intent: IntentState["intent"]): string[] {
  return [intent.market, intent.city, intent.make, ...intent.models, intent.year_min?.toString(), intent.budget_max ? `${intent.currency ?? "AED"} ${intent.budget_max.toLocaleString()}` : undefined, intent.mileage_max_km ? `${intent.mileage_max_km.toLocaleString()} km max` : undefined, ...intent.colors, ...intent.specifications, ...intent.condition_preferences].filter((value): value is string => Boolean(value));
}

function ResultCard({ match }: { match: Match }) {
  const { listing } = match;
  return <article className="result-card">
    <div className="result-heading"><div><p className="eyebrow">{listing.source_name} · {listing.city}</p><h3>{listing.title}</h3></div><strong className="score">{Math.round(match.score)}</strong></div>
    <p className="price">{listing.currency} {listing.price.toLocaleString()}</p>
    <p className="details">{listing.year} · {listing.mileage_km.toLocaleString()} km · {listing.color ?? "Color not listed"} · {listing.seller_type}</p>
    <p className="details">{listing.specifications.join(" · ") || "Specifications not listed"}{listing.warranty ? " · Warranty" : ""}</p>
    {match.reasons.length > 0 && <p className="reason">{match.reasons.join(". ")}</p>}
    {match.warnings.map((warning) => <p className="warning" key={warning}>{warning}</p>)}
    <a href={listing.source_url} target="_blank" rel="noreferrer">View source page</a>
  </article>;
}

function ComparisonTable({ matches }: { matches: Match[] }) {
  return <div className="comparison-wrap">
    <h3>Compare matches</h3>
    <table>
      <thead><tr><th>Vehicle</th><th>Price</th><th>Mileage</th><th>Specs</th><th>Condition</th><th>Source</th></tr></thead>
      <tbody>{matches.map(({ listing }) => <tr key={listing.id}>
        <td>{listing.title}</td><td>{listing.currency} {listing.price.toLocaleString()}</td><td>{listing.mileage_km.toLocaleString()} km</td>
        <td>{listing.specifications.join(", ") || "Not listed"}</td><td>{listing.condition_signals.join(". ") || "Not listed"}</td><td>{listing.source_name}</td>
      </tr>)}</tbody>
    </table>
  </div>;
}

function App() {
  const [sessionId, setSessionId] = useState<string>();
  const [intentState, setIntentState] = useState<IntentState>();
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", content: "What car are you looking for?" }]);
  const [text, setText] = useState("");
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => { createSession().then((session) => { setSessionId(session.session_id); setIntentState(session.intent_state); }).catch(() => setError("Carveo is unavailable. Start the API and try again.")); }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!sessionId || !text.trim() || loading) return;
    const content = text.trim();
    setText(""); setLoading(true); setError(undefined);
    setMessages((current) => [...current, { role: "user", content }]);
    try {
      const response = await sendMessage(sessionId, content);
      setIntentState(response.intent_state);
      setMessages((current) => [...current, response.message]);
      if (response.intent_state.ready) {
        const results = await getResults(sessionId);
        setMatches(results.matches);
      }
    } catch { setError("Carveo could not process that message. Please try again."); }
    finally { setLoading(false); }
  }

  return <main>
    <header><p className="brand">CARVEO</p><h1>Find the right used car.</h1><p className="lede">Tell us what matters. We will compare the closest matches.</p></header>
    <section className="workspace">
      <div className="chat-panel"><div className="messages">{messages.map((message, index) => <p className={`message ${message.role}`} key={`${message.role}-${index}`}>{message.content}</p>)}</div>
      {intentState && <div className="intent"><span>Search brief</span><div>{formatIntent(intentState.intent).map((tag) => <small key={tag}>{tag}</small>)}</div></div>}
      <form onSubmit={submit}><label htmlFor="message">Your search</label><textarea id="message" value={text} onChange={(event) => setText(event.target.value)} placeholder="Example: 2023 Mercedes C-Class in UAE, under AED 180k, black, GCC specs, accident-free, under 50k km" /><button disabled={!sessionId || loading}>{loading ? "Thinking" : "Send"}</button></form>
      {error && <p className="error">{error}</p>}</div>
      <div className="results-panel"><div className="results-title"><div><p className="eyebrow">Top matches</p><h2>{matches.length ? `${matches.length} matches` : "Your results will appear here"}</h2></div>{intentState?.ready && <span className="ready">Search ready</span>}</div>
      {matches.length ? <><p className="fixture-note">Fixture mode: live Dubizzle ingestion is introduced in Phase 4.</p><div className="results-grid">{matches.map((match) => <ResultCard key={match.listing.id} match={match} />)}</div><ComparisonTable matches={matches} /></> : <p className="empty">Carveo asks for a market, make, year, model or body type, budget, and two preferences before searching.</p>}</div>
    </section>
  </main>;
}

createRoot(document.getElementById("root")!).render(<App />);
