async function loadMethodology() {
  const url = `${process.env.BACKEND_URL ?? "http://localhost:8000"}/api/methodology`;
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`status ${response.status}`);
    return (await response.json()) as { version: string; section_markdown: string };
  } catch {
    return null;
  }
}

export default async function MethodologyPage() {
  const data = await loadMethodology();

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-3xl font-semibold tracking-tight">Methodology</h1>
      <p className="mt-2 text-ink/70">
        Klimaatkracht claims a specific number for every euro a buyer commits.
        That number is the output of an explicit pipeline; this page is the
        contract.
      </p>

      {data ? (
        <article className="mt-10 rounded-md border border-ink/10 bg-white px-6 py-6">
          <header className="mb-4 flex items-baseline justify-between border-b border-ink/10 pb-3">
            <h2 className="text-lg font-semibold">Methodology version</h2>
            <span className="font-mono text-sm">{data.version}</span>
          </header>
          <pre className="whitespace-pre-wrap text-sm leading-relaxed text-ink/90">
            {data.section_markdown}
          </pre>
        </article>
      ) : (
        <p className="mt-6 text-sm text-ink/60">
          Methodology endpoint unavailable — start the backend (
          <code className="font-mono">uvicorn app.main:app --reload</code>) to
          load the canonical text.
        </p>
      )}
    </div>
  );
}
