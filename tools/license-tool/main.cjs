// Electron entry for Aetheria License Generator (Admin-only)
const path = require("path");
const fs = require("fs");
const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const crypto = require("crypto");

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 980,
    height: 720,
    minWidth: 860,
    minHeight: 620,
    backgroundColor: "#0b0f14",
    title: "Aetheria — License Generator (Admin only)",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, "index.html"));
  // win.webContents.openDevTools({ mode: "detach" }); // uncomment if you want
}

/* ---------- IPC: File pickers ---------- */
ipcMain.handle("pickPrivateKey", async () => {
  const res = await dialog.showOpenDialog(win, {
    title: "Select Private Key (.bin or .pem)",
    buttonLabel: "Use this key",
    properties: ["openFile"],
    filters: [
      { name: "Keys", extensions: ["bin", "der", "pem"] },
      { name: "All Files", extensions: ["*"] },
    ],
  });
  if (res.canceled || !res.filePaths?.[0]) return { canceled: true };
  return { canceled: false, path: res.filePaths[0] };
});

/* ---------- IPC: Save JSON ---------- */
ipcMain.handle("saveJSON", async (evt, defaultName, content) => {
  const res = await dialog.showSaveDialog(win, {
    title: "Save license.json",
    defaultPath: path.join(app.getPath("desktop"), defaultName || "license.json"),
    filters: [{ name: "JSON", extensions: ["json"] }],
  });
  if (res.canceled || !res.filePath) return { canceled: true };
  fs.writeFileSync(res.filePath, content, "utf8");
  return { canceled: false, filePath: res.filePath };
});

/* ---------- IPC: Sign license with private key ---------- */
ipcMain.handle("signLicense", async (evt, licenseObj, privateKeyPath) => {
  try {
    if (!privateKeyPath) throw new Error("Private key path is empty.");
    const keyBuf = fs.readFileSync(privateKeyPath);

    // Try DER (pkcs8) first, then PEM fallback
    let privateKey;
    try {
      privateKey = crypto.createPrivateKey({ key: keyBuf, format: "der", type: "pkcs8" });
    } catch {
      privateKey = crypto.createPrivateKey({ key: keyBuf, format: "pem" });
    }

    const payload = Buffer.from(JSON.stringify(licenseObj));
    const signer = crypto.createSign("sha256");
    signer.update(payload);
    signer.end();
    const sig = signer.sign(privateKey); // Buffer
    return { ok: true, signatureHex: sig.toString("hex") };
  } catch (err) {
    return { ok: false, error: err.message || String(err) };
  }
});

app.whenReady().then(createWindow);
app.on("window-all-closed", () => app.quit());
