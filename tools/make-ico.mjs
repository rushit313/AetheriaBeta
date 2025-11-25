import fs from "fs";
import path from "path";
import pngToIco from "png-to-ico";

const root = process.cwd();
const png = path.join(root, "build", "icon.png");
const out = path.join(root, "build", "icon.ico");

if (!fs.existsSync(png)) {
  console.error("❌ build/icon.png not found. Export a 1024x1024 PNG first.");
  process.exit(1);
}

const sizes = [256, 128, 64, 48, 32, 16];

(async () => {
  try {
    const buf = await pngToIco(png, { sizes });
    fs.writeFileSync(out, buf);
    console.log("✅ Generated build/icon.ico");
  } catch (e) {
    console.error("❌ Failed to generate ICO:", e.message);
    process.exit(1);
  }
})();
