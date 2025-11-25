import React, { useEffect, useState } from "react";

type Health = { ok: boolean; service?: string } | null;

export default function BackendStatus({
  baseUrl = "http://127.0.0.1:5001",
  intervalMs = 2000,
}: {
  baseUrl?: string;
  intervalMs?: number;
}) {
  const [health, setHealth] = useState<Health>(null);

  async function poll() {
    try {
      const res = await fetch(`${baseUrl}/api/ping`, { cache: "no-store" });
      if (!res.ok) throw new Error("bad status");
      const data = await res.json();
      setHealth(data);
    } catch {
      setHealth({ ok: false });
    }
  }

  useEffect(() => {
    poll();
    const t = setInterval(poll, intervalMs);
    return () => clearInterval(t);
  }, []);

  const ok = !!health?.ok;

  return (
    <div className="status">
      <span className={`dot ${ok ? "ok" : "bad"}`} />
      <span className="label">{ok ? "Online" : "Offline"}</span>
      <style>{`
        .status { display:inline-flex; align-items:center; gap:8px; font: 500 14px system-ui, -apple-system, Segoe UI, Roboto, Arial; }
        .dot { width:10px; height:10px; border-radius:50%; background:#d33; box-shadow:0 0 0 2px rgba(0,0,0,.04) inset; }
        .dot.ok { background:#16a34a; }
        .label { opacity:.9 }
      `}</style>
    </div>
  );
}
