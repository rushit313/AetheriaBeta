import React, { useMemo, useRef, useState } from "react";
import { Capacitor } from "@capacitor/core";
import "./app.css";

/** Backend base */
const getPlatformBackend = () => {
  if (Capacitor.getPlatform() === 'android') {
    // For Android emulator: use 10.0.2.2
    // For physical device: use your computer's IP (e.g., 192.168.0.109)
    // Change via Settings (⚙️) button if needed
    return "http://10.0.2.2:5001";
  }
  return "http://127.0.0.1:5001";
};

const DEFAULT_BACKEND =
  window.__AETHERIA_BACKEND__ ||
  localStorage.getItem("aetheria_backend") ||
  process.env.AETHERIA_BACKEND ||
  getPlatformBackend();

/* ---------- small utils ---------- */
const asNum = (v, n = 2) => (typeof v === "number" ? v.toFixed(n) : String(v));

function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/* ---------- upload widgets ---------- */
function UploadBox({ label, file, onFile }) {
  const inputRef = useRef();

  const onDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer?.files?.[0];
    if (f) onFile(f);
  };

  return (
    <div
      className="drop glass-panel"
      onDragOver={(e) => e.preventDefault()}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
    >
      <div style={{ marginBottom: 12, fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>{label}</div>
      <div className="muted">Drag &amp; drop, or click to select</div>
      <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>PNG, JPG, WEBP up to 10MB</div>
      <input
        ref={inputRef}
        hidden
        type="file"
        accept="image/*"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
        }}
      />
      {file && <div style={{ marginTop: 12, color: 'var(--accent-primary)', fontWeight: 600 }}>Selected: {file.name}</div>}
    </div>
  );
}

/* ---------- chips ---------- */
function PaletteChips({ title, palette }) {
  const chips = (palette || []).slice(0, 8);
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      {chips.length ? (
        <div className="chip-row">
          {chips.map((p, i) => (
            <div className="chip" key={i} title={p.hex}>
              <span className="chip-dot" style={{ background: p.hex || "#888" }} />
              <span className="chip-hex">{p.hex}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="muted">None</div>
      )}
    </div>
  );
}

/* ---------- Image Overlay Component ---------- */
function ImageOverlay({ title, file, textures, palette, metrics, score, critique }) {
  const [url, setUrl] = useState(null);

  React.useEffect(() => {
    if (!file) return;
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);

  if (!file || !url) return null;

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="card-title" style={{ marginBottom: 0 }}>{title}</div>
        {score !== undefined && (
          <div style={{
            background: `conic-gradient(var(--success) ${score}%, #e2e8f0 0)`,
            width: 40, height: 40, borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            position: 'relative'
          }}>
            <div style={{
              width: 32, height: 32, background: '#fff', borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 12, fontWeight: 700, color: 'var(--text-primary)'
            }}>
              {score}
            </div>
          </div>
        )}
      </div>

      <div className="overlay-container">
        <img className="main-image" src={url} alt="render" />

        {/* Texture Markers */}
        {textures && textures.map((t, i) => (
          <div
            key={i}
            className="marker"
            style={{
              left: `${t.x || 50}%`,
              top: `${t.y || 50}%`
            }}
          >
            {/* Floating Card */}
            <div className="callout-card">
              <div style={{ display: 'flex', gap: 12 }}>
                <img className="callout-image" style={{ width: 60, height: 60 }} src={t.texture_url} alt={t.name} />
                {t.suggestion_url && (
                  <>
                    <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-secondary)' }}>→</div>
                    <img className="callout-image" style={{ width: 60, height: 60, borderColor: 'var(--success)' }} src={t.suggestion_url} alt="Suggestion" />
                  </>
                )}
              </div>

              <div className="callout-title">{t.name}</div>
              <div className="callout-meta">
                {t.suggestion ? (
                  <div style={{ color: 'var(--success)', fontWeight: 600, marginBottom: 4 }}>
                    Suggestion: {t.suggestion}
                  </div>
                ) : (
                  t.hex && <div style={{ color: t.hex, marginBottom: 4, fontWeight: 600 }}>{t.hex}</div>
                )}

                {t.note && <div>{t.note}</div>}

                {t.link && (
                  <a
                    href={t.link}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      display: 'inline-block',
                      marginTop: 8,
                      background: 'var(--accent-primary)',
                      color: '#fff',
                      padding: '4px 12px',
                      borderRadius: 6,
                      textDecoration: 'none',
                      fontSize: 12,
                      fontWeight: 600
                    }}
                  >
                    Download Texture
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Palette Overlay (Bottom Left) */}
        {palette && palette.length > 0 && (
          <div style={{
            position: 'absolute',
            bottom: 20,
            left: 20,
            background: 'rgba(255,255,255,0.9)',
            padding: '8px',
            borderRadius: '12px',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
          }}>
            <div style={{ display: 'flex', gap: 6 }}>
              {palette.map((p, i) => (
                <div key={i} title={p.hex} style={{
                  width: 20,
                  height: 20,
                  borderRadius: '50%',
                  background: p.hex,
                  border: '2px solid #fff',
                  boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
                }} />
              ))}
            </div>
          </div>
        )}

        {/* Metrics Overlay (Top Right) */}
        {metrics && (
          <div style={{
            position: 'absolute',
            top: 20,
            right: 20,
            background: 'rgba(255,255,255,0.9)',
            padding: '12px',
            borderRadius: '12px',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
            fontSize: 11,
            minWidth: 120
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, marginBottom: 6, color: 'var(--text-secondary)' }}>METRICS</div>
            {Object.entries(metrics).map(([k, v]) => (
              v !== null && typeof v !== 'object' && (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                  <span style={{ opacity: 0.7 }}>{k.split('_')[0]}</span>
                  <span style={{ fontWeight: 600 }}>{asNum(v)}</span>
                </div>
              )
            ))}
          </div>
        )}
      </div>

      {/* Critique Section */}
      {critique && (
        <div style={{ marginTop: 16, padding: 16, background: 'rgba(255,255,255,0.5)', borderRadius: 12, border: '1px solid var(--glass-border)' }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 4, textTransform: 'uppercase' }}>AI Critique</div>
          <div style={{ fontSize: 14, lineHeight: 1.5, color: 'var(--text-primary)' }}>{critique}</div>
        </div>
      )}
    </div>
  );
}

/* ---------- Workflow Checklist ---------- */
function WorkflowChecklist({ analysis, lighting }) {
  const [checked, setChecked] = useState({});

  const steps = useMemo(() => {
    const s = [
      { id: "upload", label: "Upload Render & Reference", done: true },
      { id: "analyze", label: "Run AI Analysis", done: true },
    ];

    if (analysis) {
      s.push({ id: "textures", label: "Download Suggested Textures", done: false });
      if (lighting && lighting.length > 0) {
        s.push({ id: "lighting", label: "Adjust Lighting Setup", done: false });
      }
      s.push({ id: "export", label: "Export Material Board", done: false });
    }
    return s;
  }, [analysis, lighting]);

  const toggle = (id) => setChecked(p => ({ ...p, [id]: !p[id] }));

  return (
    <div className="card workflow-card">
      <div className="card-title">Smart Workflow</div>
      <div className="checklist">
        {steps.map(s => (
          <div key={s.id} className={`checklist-item ${s.done || checked[s.id] ? "done" : ""}`} onClick={() => !s.done && toggle(s.id)}>
            <div className="checkbox">{s.done || checked[s.id] ? "✓" : ""}</div>
            <span>{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- Lighting Advisor ---------- */
function LightingAdvisor({ suggestions }) {
  if (!suggestions || suggestions.length === 0) return null;
  return (
    <div className="card">
      <div className="card-title">Lighting Advisor</div>
      <div className="lighting-grid">
        {suggestions.map((s, i) => (
          <div key={i} className="lighting-card">
            <div className="lighting-type">{s.type}</div>
            <div className="lighting-suggestion">{s.suggestion}</div>
            <div className="lighting-action">{s.action}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- main ---------- */
export default function App() {
  const [backendUrl, setBackendUrl] = useState(DEFAULT_BACKEND);
  const [showSettings, setShowSettings] = useState(false);

  const [useAI, setUseAI] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);

  const [renderFile, setRenderFile] = useState(null);
  const [refFile, setRefFile] = useState(null);

  const [result, setResult] = useState(null);

  const renderPalette = useMemo(() => result?.analysis?.palette || [], [result]);
  const referencePalette = useMemo(
    () => result?.analysis_ref?.palette || [],
    [result]
  );

  const renderTextures = useMemo(() => result?.render_textures || [], [result]);
  const referenceTextures = useMemo(
    () => result?.reference_textures || [],
    [result]
  );
  const differences = useMemo(() => result?.differences || [], [result]);
  const lightingSuggestions = useMemo(() => result?.lighting_suggestions || [], [result]);

  const analyze = async () => {
    if (!renderFile) {
      setMsg({ type: "err", text: "Please upload your render image first." });
      return;
    }

    try {
      console.log("[Aetheria] Starting analysis...");
      console.log("[Aetheria] Backend URL:", backendUrl);
      setBusy(true);
      setMsg(null);

      const fd = new FormData();
      fd.append("render", renderFile);
      if (refFile) fd.append("reference", refFile);
      fd.append("ai", useAI ? "1" : "0");

      console.log("[Aetheria] Sending request to:", `${backendUrl}/api/analyze_render`);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const r = await fetch(`${backendUrl}/api/analyze_render`, {
        method: "POST",
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      console.log("[Aetheria] Response status:", r.status);

      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();

      console.log("[Aetheria] Response data:", data);

      const safeAnalysis = {
        exposure_mean: data?.analysis?.exposure_mean ?? null,
        contrast_std: data?.analysis?.contrast_std ?? null,
        noise_level: data?.analysis?.noise_level ?? null,
        palette: Array.isArray(data?.analysis?.palette) ? data.analysis.palette.slice(0, 6) : [],
        saturation_pct: data?.analysis?.saturation_pct ?? null,
        sharpness_laplacian_var: data?.analysis?.sharpness_laplacian_var ?? null,
        wb_shift_blue_minus_red: data?.analysis?.wb_shift_blue_minus_red ?? null,
      };

      setResult({
        ...data,
        analysis: safeAnalysis,
      });
      setMsg({ type: "ok", text: "Analysis complete." });
      console.log("[Aetheria] Analysis complete!");
    } catch (e) {
      console.error("[Aetheria] Analysis error:", e);
      if (e.name === 'AbortError') {
        setMsg({ type: "err", text: `Request timeout. Is the backend running at ${backendUrl}?` });
      } else {
        setMsg({ type: "err", text: `Analyze failed: ${e.message}` });
      }
    } finally {
      setBusy(false);
    }
  };

  const ping = async () => {
    try {
      const r = await fetch(`${backendUrl}/api/ping`);
      const j = await r.json();
      setMsg({ type: "ok", text: `Ping OK · ${JSON.stringify(j)}` });
    } catch {
      setMsg({ type: "err", text: "Ping failed" });
    }
  };

  const exportD5 = () => {
    const preset = {
      version: 1,
      meta: { generator: "Aetheria", note: "Placeholder preset" },
      grading: { exposure: 0.05, contrast: 0.15, bloom: 0.2, temperature: 0.0 },
    };
    downloadText("aetheria.d5pp", JSON.stringify(preset, null, 2));
  };

  const exportLumion = () => {
    const stack = {
      LumionEffectStack9: {
        Exposure: 0.05,
        Contrast: 0.15,
        Bloom: 0.2,
        Temperature: 0.0,
      },
    };
    downloadText("aetheria.ls9", JSON.stringify(stack, null, 2));
  };

  const exportMaterialBoard = () => {
    if (!result) return;
    const content = `
      <html>
      <head><title>Material Board - Aetheria</title></head>
      <body style="font-family: sans-serif; padding: 40px;">
        <h1>Material Board</h1>
        <h2>Palette</h2>
        <div style="display: flex; gap: 10px;">
          ${renderPalette.map(p => `<div style="width: 50px; height: 50px; background: ${p.hex};"></div>`).join('')}
        </div>
        <h2>Suggested Textures</h2>
        <ul>
          ${renderTextures.map(t => `
            <li>
              <strong>${t.name}</strong>: Suggested <a href="${t.suggestion_url}">${t.suggestion}</a>
              <br/>Link: <a href="${t.link}">${t.link}</a>
            </li>
          `).join('')}
        </ul>
        <h2>Lighting Advice</h2>
        <ul>
          ${lightingSuggestions.map(l => `<li><strong>${l.type}</strong>: ${l.suggestion} (${l.action})</li>`).join('')}
      </html>
    `;
    downloadText("material_board.html", content);
  };

  /* ---------- AI Generation ---------- */
  const [generating, setGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);

  const generateAI = async () => {
    if (!renderFile) return;
    try {
      setGenerating(true);
      const fd = new FormData();
      fd.append("render", renderFile);

      const r = await fetch(`${backendUrl}/api/generate_render`, { method: "POST", body: fd });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();

      if (data.ok) {
        setGeneratedImage(data.image_url);
        setMsg({ type: "ok", text: "AI Enhancement Complete!" });
      } else {
        throw new Error(data.error || "Unknown error");
      }
    } catch (e) {
      console.error(e);
      setMsg({ type: "err", text: `Generation failed: ${e.message}` });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="app">
      <header className="top">
        <div className="brand"><span className="icon">✨</span> Aetheria</div>
        <div className="toolbar-scroll">
          <div className="toolbar">
            <button className="btn btn-primary" onClick={analyze} disabled={busy}>
              {busy ? "Analyzing…" : "Analyze Render"}
            </button>
            <button className="btn btn-accent" onClick={generateAI} disabled={generating || !renderFile}>
              {generating ? "Enhancing…" : "✨ Generate AI"}
            </button>
            <button className="btn" onClick={exportD5}>Export D5</button>
            <button className="btn" onClick={exportLumion}>Export Lumion</button>
            {result && <button className="btn" onClick={exportMaterialBoard}>Export Board</button>}
            <label className="toggle-btn">
              <input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} />
              <span>AI Critique</span>
            </label>
            <button className="btn" onClick={ping}>Test API</button>
            <button className="btn" onClick={() => setShowSettings(true)}>⚙️</button>
          </div>
        </div>
      </header>

      <main className="content">
        <div className="grid-layout">
          <div className="main-column">
            <div className="grid-2">
              <UploadBox label="1. Upload Render" file={renderFile} onFile={setRenderFile} />
              <UploadBox label="2. Upload Reference (Optional)" file={refFile} onFile={setRefFile} />
            </div>

            {result && (
              <>
                {/* Image Overlays with Integrated Feedback */}
                <div className="grid-2">
                  <ImageOverlay
                    title="Render Analysis"
                    file={renderFile}
                    textures={renderTextures}
                    palette={renderPalette}
                    metrics={result?.analysis}
                    score={result?.score}
                    critique={result?.critique}
                  />
                  {refFile && (
                    <ImageOverlay
                      title="Reference Analysis"
                      file={refFile}
                      textures={referenceTextures}
                      palette={referencePalette}
                    />
                  )}
                </div>

                {/* Lighting Advisor */}
                <LightingAdvisor suggestions={lightingSuggestions} />

                {/* Differences (Only if detected) */}
                {differences?.length > 0 && (
                  <div className="card">
                    <div className="card-title">Differences Detected</div>
                    <ul style={{ paddingLeft: 20, lineHeight: 1.6 }}>
                      {differences.map((d, i) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Sidebar */}
          <div className="sidebar">
            <WorkflowChecklist analysis={result} lighting={lightingSuggestions} />
          </div>
        </div>
      </main>

      {/* AI Generation Modal */}
      {generatedImage && (
        <div className="modal-backdrop" onClick={() => setGeneratedImage(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="card-title" style={{ marginBottom: 0 }}>AI Enhanced Render</div>
              <button className="btn-close" onClick={() => setGeneratedImage(null)}>×</button>
            </div>
            <div className="modal-body">
              <img src={generatedImage} alt="AI Generated" className="generated-image" />
            </div>
            <div className="modal-footer">
              <a href={generatedImage} download="aetheria_enhanced.jpg" className="btn btn-primary">
                Download High-Res
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-backdrop" onClick={() => setShowSettings(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="card-title" style={{ marginBottom: 0 }}>Settings</div>
              <button className="btn-close" onClick={() => setShowSettings(false)}>×</button>
            </div>
            <div className="modal-body">
              <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>Backend URL</label>
              <input
                type="text"
                value={backendUrl}
                onChange={(e) => {
                  setBackendUrl(e.target.value);
                  localStorage.setItem("aetheria_backend", e.target.value);
                }}
                style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ccc' }}
              />
              <div style={{ fontSize: 12, color: '#666', marginTop: 8 }}>
                For mobile, use your computer's local IP (e.g., http://192.168.1.5:5001)
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-primary" onClick={() => setShowSettings(false)}>Done</button>
            </div>
          </div>
        </div>
      )}

      {msg && (
        <div className={`toast ${msg.type === "err" ? "toast-err" : "toast-ok"}`}>
          {msg.text}
        </div>
      )}
    </div>
  );
}
