// tools/generate-keys.mjs
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import crypto from "crypto";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Where to save
const outDir = path.resolve(__dirname, "..", "admin-secure");
fs.mkdirSync(outDir, { recursive: true });

// Generate 2048-bit RSA keypair
const { privateKey, publicKey } = crypto.generateKeyPairSync("rsa", {
  modulusLength: 2048,
});

// Export as DER (binary) in correct types
const privDer = privateKey.export({ type: "pkcs8", format: "der" });
const pubDer  = publicKey.export({ type: "spki",  format: "der"  });

const privPath = path.join(outDir, "private_key.bin");
const pubPath  = path.join(outDir, "public_key.bin");

fs.writeFileSync(privPath, Buffer.from(privDer));
fs.writeFileSync(pubPath,  Buffer.from(pubDer));

console.log("✅ Wrote:");
console.log("  ", privPath);
console.log("  ", pubPath);
console.log("Note: DO NOT open/save these in a text editor.");
