export default function LocaleLoading() {
  return <main className="min-h-screen bg-marble"><div className="shell py-12"><div className="h-4 w-28 animate-pulse bg-muted" /><div className="mt-4 h-12 w-2/3 max-w-xl animate-pulse bg-muted" /><div className="mt-10 grid gap-4 md:grid-cols-3">{Array.from({ length: 6 }, (_, index) => <div key={index} className="aspect-[4/3] animate-pulse bg-muted" />)}</div></div></main>;
}
