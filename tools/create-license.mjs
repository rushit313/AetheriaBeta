// tools/create-license.mjs
import { readFileSync, writeFileSync, mkdirSync } from "fs";
import crypto from "crypto";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname  = dirname(__filename);
const rootDir    = dirname(__dirname);

// --- CONFIG ---
const PRIVATE_KEY_PATH = join(rootDir, "tools", "private_key.bin");
const OUTPUT_DIR       = join(rootDir, "licenses");  // where license files are saved

// Ensure license folder exists
mkdirSync(OUTPUT_DIR, { recursive: true });

// --- INPUTS ---
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error("Usage: node tools/create-license.mjs <MACHINE_ID> <USERNAME>");
  process.exit(1);
}

const [machineId, username] = args;
const privateKey = readFileSync(PRIVATE_KEY_PATH);

// --- LICENSE PAYLOAD ---
const payload = {
  machineId,
  username,
  issuedAt: new Date().toISOString(),
  expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year
};

// --- SIGN LICENSE (HMAC using private key) ---
const signature = crypto
  .createHmac("sha256", privateKey)
  .update(JSON.stringify(payload))
  .digest("hex");

const licenseData = {
  ...payload,
  signature,
};

const fileName = `${username}-${machineId}.lic`;
const outputPath = join(OUTPUT_DIR, fileName);

writeFileSync(outputPath, JSON.stringify(licenseData, null, 2));

console.log("✅ License created successfully!");
console.log("File:", outputPath);
console.log("\n--- License Preview ---\n", JSON.stringify(licenseData, null, 2));
