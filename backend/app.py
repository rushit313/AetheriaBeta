import argparse, io, os
from typing import List, Tuple
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Optional: light palette sniff if Pillow is present
try:
    from PIL import Image, ImageOps, ImageFilter
    PIL_OK = True
except Exception:
    PIL_OK = False

# Import AI modules
try:
    from material_db import generate_texture_suggestions
    from ai_vision import analyze_image_with_ai, get_material_category
    AI_MODULES_OK = True
except Exception as e:
    print(f"Warning: AI modules not available: {e}")
    AI_MODULES_OK = False

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024  # 12MB

# ---------------- helpers ----------------
def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"

def quick_palette(img_bytes: bytes, k: int = 6) -> List[dict]:
    """
    Very small, robust palette extractor.
    - If Pillow is available, quantize & return top k colors.
    - Otherwise return a fixed pleasant set.
    """
    if not PIL_OK:
        return [{"hex": h} for h in ["#1e293b", "#94a3b8", "#38bdf8", "#f59e0b", "#10b981"]][:k]

    try:
        im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        # shrink for speed, quantize to many colors then take top k
        im = im.resize((min(256, im.width), min(256, im.height)))
        pal = im.quantize(colors=max(16, k * 3), method=Image.MEDIANCUT)
        # build histogram of palette indices
        hist = pal.histogram()
        # map palette idx -> rgb
        pal_img = pal.getpalette()  # flat list
        def idx_to_rgb(idx):
            base = idx * 3
            return pal_img[base], pal_img[base + 1], pal_img[base + 2]
        # sort by frequency desc
        top = sorted(range(len(hist)), key=lambda i: hist[i], reverse=True)[:k]
        hexes = []
        seen = set()
        for i in top:
            hx = rgb_to_hex(idx_to_rgb(i))
            # dedupe close repeats
            if hx not in seen:
                seen.add(hx)
                hexes.append({"hex": hx})
        return hexes[:k]
    except Exception:
        # fallback if anything goes wrong
        return [{"hex": h} for h in ["#1e293b", "#94a3b8", "#38bdf8", "#f59e0b", "#10b981"]][:k]

# -------------- routes -------------------
@app.get("/api/ping")
def ping():
    return jsonify(ok=True, service="Aetheria Backend")

@app.post("/api/analyze_render")
def analyze_render():
    """
    Accepts:
      - render: required image
      - reference: optional image
      - ai: "1" or "0" (toggle for AI analysis)
    Returns JSON with palettes, texture callouts, and AI critique.
    """
    render_file = request.files.get("render")
    if not render_file:
        return jsonify(error="Missing file field 'render'"), 400

    render_bytes = render_file.read()
    ref_file = request.files.get("reference")
    ref_bytes = ref_file.read() if ref_file else None
    
    use_ai = request.form.get("ai") == "1"

    # Palettes
    render_palette = quick_palette(render_bytes, k=6)
    ref_palette = quick_palette(ref_bytes, k=6) if ref_bytes else []

    # Basic image analysis (mocked for speed, can be replaced with OpenCV if needed)
    analysis = {
        "exposure_mean": 120.8,
        "contrast_std": 52.2,
        "noise_level": 7.7,
        "palette": render_palette,
        "saturation_pct": 28.3,
        "sharpness_laplacian_var": 1726,
        "wb_shift_blue_minus_red": -15.5,
    }

    # Optional reference analysis
    analysis_ref = {"palette": ref_palette} if ref_bytes else {}

    # --- AI Analysis ---
    render_textures = []
    critique = None
    score = 75 # Default score
    
    if use_ai and AI_MODULES_OK:
        print("Starting AI analysis...")
        ai_result = analyze_image_with_ai(render_bytes)
        
        if ai_result.get('success'):
            # Process materials
            raw_materials = ai_result.get('materials', [])
            
            # Convert to frontend format
            from material_db import MATERIAL_DATABASE
            
            for i, mat in enumerate(raw_materials):
                # Get suggestion from local DB based on detected type
                mat_type = mat.get('type', 'concrete')
                category = get_material_category(mat_type)
                
                # Look up in DB
                mat_entry = MATERIAL_DATABASE.get(category, {})
                textures = mat_entry.get('textures', [])
                suggestion_data = textures[0] if textures else {}
                
                render_textures.append({
                    "name": mat.get('name', f"Material {i+1}"),
                    "type": mat_type,
                    "x": 50 + (i * 10) % 40, # Mock position if not provided
                    "y": 50 + (i * 10) % 40,
                    "hex": mat.get('color', '#cccccc'),
                    "suggestion": suggestion_data.get('suggestion', 'Standard Finish'),
                    "suggestion_url": suggestion_data.get('suggestion_url', ''),
                    "link": suggestion_data.get('link', '#'),
                    "texture_url": "https://via.placeholder.com/60?text=Detected", # Placeholder for detected crop
                    "note": f"Detected {mat_type}"
                })
            
            # Extract critique from raw response if available or generate one
            # For now, we'll use a simple generated one based on findings
            material_names = [m.get('name', 'unknown') for m in raw_materials]
            critique = f"AI Analysis detected the following materials: {', '.join(material_names)}. " \
                       f"Consider refining the textures for {material_names[0] if material_names else 'surfaces'} to match the reference style."
            score = 85
        else:
            print(f"AI Analysis failed: {ai_result.get('error')}")
            critique = "AI Analysis failed to process the image. Please check your API key."

    # --- Fallback / Mock Data if AI not used or failed ---
    if not render_textures:
        # Keep some mock data so the UI isn't empty during testing without API key
        render_textures = [
            {
                "name": "Floor (Mock)",
                "type": "wood",
                "x": 50, "y": 80,
                "hex": "#8b5a2b",
                "suggestion": "Oak Plank Natural",
                "suggestion_url": "https://images.unsplash.com/photo-1516455590571-18256e5bb9ff?auto=format&fit=crop&w=64&q=80",
                "link": "https://www.poliigon.com/texture/wood-flooring-001",
                "texture_url": "https://via.placeholder.com/60/8b5a2b/ffffff?text=Floor",
                "note": "Too smooth, needs bump map"
            }
        ]
        if use_ai:
             critique = critique or "Could not detect specific materials. Using fallback data."

    # --- Lighting Analysis ---
    lighting_suggestions = []
    if analysis["exposure_mean"] < 100:
        lighting_suggestions.append({
            "type": "Exposure",
            "suggestion": "Increase global exposure or add fill lights.",
            "action": "Adjust Exposure +0.5EV"
        })
    elif analysis["exposure_mean"] > 180:
        lighting_suggestions.append({
            "type": "Exposure",
            "suggestion": "Reduce exposure to prevent blown-out highlights.",
            "action": "Adjust Exposure -0.5EV"
        })

    if analysis["contrast_std"] < 40:
        lighting_suggestions.append({
            "type": "Contrast",
            "suggestion": "Lighting is too flat. Add directional light.",
            "action": "Increase Contrast"
        })

    return jsonify(
        analysis=analysis,
        analysis_ref=analysis_ref,
        render_textures=render_textures,
        reference_textures=[], # Reference textures not implemented yet
        differences=[], # Differences not implemented yet
        score=score,
        critique=critique,
        lighting_suggestions=lighting_suggestions
    )

@app.post("/api/generate_render")
def generate_render():
    """
    Simulates an AI re-render by upscaling and enhancing the image.
    """
    render_file = request.files.get("render")
    if not render_file:
        return jsonify(error="Missing file field 'render'"), 400

    if not PIL_OK:
        return jsonify(error="Server missing PIL library"), 500

    try:
        # Read image
        img = Image.open(render_file).convert("RGB")
        
        # 1. Upscale (1.5x)
        new_size = (int(img.width * 1.5), int(img.height * 1.5))
        img = img.resize(new_size, Image.LANCZOS)
        
        # 2. Auto Contrast
        img = ImageOps.autocontrast(img, cutoff=1)
        
        # 3. Sharpen
        img = img.filter(ImageFilter.SHARPEN)
        
        # Return as base64
        import base64
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        
        return jsonify(
            ok=True,
            image_url=f"data:image/jpeg;base64,{b64}",
            message="AI Enhancement Complete"
        )
    except Exception as e:
        return jsonify(error=str(e)), 500

# -------------- entry --------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.getenv("AETHERIA_PORT", "5001")))
    args = parser.parse_args()
    print(f"Starting Aetheria Backend on http://0.0.0.0:{args.port}")
    print(f"Access from this computer: http://127.0.0.1:{args.port}")
    print(f"Access from Android emulator: http://10.0.2.2:{args.port}")
    app.run(host="0.0.0.0", port=args.port, use_reloader=False)

if __name__ == "__main__":
    main()
