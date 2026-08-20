import Link from "next/link";

export default function NotFound() {
  return <main className="min-h-screen bg-obsidian text-white"><div className="shell py-24"><p className="text-xs font-semibold uppercase text-signal">404</p><h1 className="font-display mt-3 text-6xl font-semibold uppercase">This road ends here</h1><p className="mt-4 text-sm text-white/65">The page or fixture listing is unavailable.</p><Link href="/en-ae" className="mt-8 inline-flex h-10 items-center bg-signal px-4 text-sm font-semibold text-obsidian">Return home</Link></div></main>;
}
