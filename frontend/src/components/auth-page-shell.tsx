import Link from "next/link";

type AuthPageShellProps = {
  children: React.ReactNode;
  eyebrow: string;
  title: string;
};

export function AuthPageShell({ children, eyebrow, title }: AuthPageShellProps) {
  return (
    <main className="grid min-h-screen bg-obsidian text-white lg:grid-cols-[minmax(0,1fr)_minmax(420px,0.72fr)]">
      <section className="flex min-h-[42vh] flex-col justify-between border-b border-white/15 p-6 lg:min-h-screen lg:border-r lg:border-b-0 lg:p-12">
        <Link href="/en-ae" className="w-fit font-display text-4xl font-semibold uppercase">
          Carveo<span className="text-signal">.</span>
        </Link>
        <div className="max-w-2xl py-12 lg:py-0">
          <p className="mb-5 text-sm font-semibold uppercase text-signal">{eyebrow}</p>
          <h1 className="font-display text-5xl font-semibold uppercase leading-[0.94] sm:text-7xl lg:text-8xl">
            {title}
          </h1>
          <p className="mt-6 max-w-xl text-base leading-7 text-white/65">
            Keep shortlisted cars, comparisons, saved searches, and future AI conversations tied to one private buyer profile.
          </p>
        </div>
        <p className="text-xs text-white/45">UAE marketplace discovery by Carveo</p>
      </section>
      <section className="flex items-center justify-center bg-marble px-4 py-12 text-obsidian sm:px-8">
        {children}
      </section>
    </main>
  );
}
