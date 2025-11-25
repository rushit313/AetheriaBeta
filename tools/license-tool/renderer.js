// Front-end logic for the License Generator
const $ = (id) => document.getElementById(id);
const setStatus = (msg, type = "") => {
  const n = $("status");
  n.textContent = msg;
  n.className = "status " + (type || "");
};

let selectedKeyPath = "";

function computeExpiry(days, explicitISO) {
  if (explicitISO && explicitISO.trim()) return explicitISO.trim();
  const d = new Date();
  const add = parseInt(days || "365", 10);
  d.setDate(d.getDate() + (isNaN(add) ? 365 : add));
  return d.toISOString();
}

$("btnPickKey").addEventListener("click", async () => {
  try {
    setStatus("Opening file picker…");
    const res = await window.api.pickPrivateKey();
    if (res.canceled) {
      setStatus("Private key not selected.");
      return;
    }
    selectedKeyPath = res.path;
    $("privateKeyPath").textContent = selectedKeyPath.split(/[\\/]/).pop();
    setStatus("Private key selected.", "ok");
  } catch (err) {
    setStatus(`Error: ${err.message || err}`, "error");
  }
});

$("btnGenerate").addEventListener("click", async () => {
  const machineId = $("machineId").value.trim();
  const staffName = $("staffName").value.trim();
  const days = $("days").value.trim();
  const iso = $("iso").value.trim();

  if (!machineId) return setStatus("Please paste a Machine ID from the staff PC.", "error");
  if (!staffName) return setStatus("Please enter User/Staff name.", "error");
  if (!selectedKeyPath) return setStatus("Pick a private key first.", "error");

  const license = {
    machineId,
    username: staffName,
    issuedAt: new Date().toISOString(),
    expiresAt: computeExpiry(days, iso),
  };

  setStatus("Signing license…");
  const res = await window.api.signLicense(license, selectedKeyPath);
  if (!res.ok) {
    setStatus(`Sign error: ${res.error}`, "error");
    return;
  }
  license.signature = res.signatureHex;
  const pretty = JSON.stringify(license, null, 2);
  $("preview").value = pretty;
  setStatus("License generated. You can Save As…", "ok");
});

$("btnSave").addEventListener("click", async () => {
  const content = $("preview").value.trim();
  if (!content || content === "{}") {
    setStatus("Nothing to save. Generate a license first.", "error");
    return;
  }
  setStatus("Saving file…");
  const res = await window.api.saveJSON("license.json", content);
  if (res.canceled) {
    setStatus("Save cancelled.");
  } else {
    setStatus(`Saved: ${res.filePath}`, "ok");
  }
});

// Quality-of-life shortcuts
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
    e.preventDefault();
    $("btnSave").click();
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "g") {
    e.preventDefault();
    $("btnGenerate").click();
  }
});

// Optional: pre-fill status on boot
window.api.ping?.().then(() => setStatus("Ready."));
