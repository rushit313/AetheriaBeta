// Preload: safe bridge exposed to the renderer
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  pickPrivateKey: () => ipcRenderer.invoke("pickPrivateKey"),
  signLicense: (licenseObj, privateKeyPath) => ipcRenderer.invoke("signLicense", licenseObj, privateKeyPath),
  saveJSON: (defaultName, content) => ipcRenderer.invoke("saveJSON", defaultName, content),
  ping: () => Promise.resolve("pong"),
});
