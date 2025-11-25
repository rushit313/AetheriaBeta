import argparse, io, os
from typing import List, Tuple
from flask import Flask, jsonify, request
from flask_cors import CORS

# Optional: light palette sniff if Pillow is present
try:
    from PIL import Image, ImageOps, ImageFilter
    PIL_OK = True
except Exception:
    PIL_OK = False

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
      - ai: "1" or "0" (ignored here; front-end toggle preserved)
    Returns JSON the front-end expects (palettes + texture callouts).
    """
    render_file = request.files.get("render")
    if not render_file:
        return jsonify(error="Missing file field 'render'"), 400

    render_bytes = render_file.read()
    ref_file = request.files.get("reference")
    ref_bytes = ref_file.read() if ref_file else None

    # Palettes
    render_palette = quick_palette(render_bytes, k=6)
    ref_palette = quick_palette(ref_bytes, k=6) if ref_bytes else []

    # Minimal analysis numbers (mocked / safe defaults)
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

    # --- Scoring & Critique Logic ---
    # In a real app, compare analysis vs analysis_ref metrics.
    # Here we mock a "Realism Score" and critique.
    score = 72  # 0-100
    critique = (
        "The render has good composition but lacks the contrast depth of the reference. "
        "The lighting feels a bit flat, and the wood textures are too smooth. "
        "Increasing the ambient occlusion and using higher-roughness maps for the floor would improve realism."
    )

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
    
    # Mock HDRI suggestion
    lighting_suggestions.append({
        "type": "HDRI",
        "suggestion": "Use a 'Golden Hour' HDRI for warmer tones.",
        "action": "Set HDRI: Golden Hour"
    })

    # ----- Texture callouts -----
    # Enhanced with "suggestions" for the render
    # Enhanced with "suggestions" for the render
    render_textures = [
        {
            "name": "Floor Wood",
            "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/wood_cabinet_worn/wood_cabinet_worn_diff_2k.jpg",
            "hex": "#8b6a4b",
            "x": 40,
            "y": 80,
            "suggestion": "Walnut Brown",
            "suggestion_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/walnut_veneer/walnut_veneer_diff_2k.jpg",
            "link": "https://polyhaven.com/a/walnut_veneer"
        },
        {
            "name": "Ceiling Plaster",
            "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/plaster_grey/plaster_grey_diff_2k.jpg",
            "hex": "#e5e5e5",
            "x": 50,
            "y": 15,
            "suggestion": "Rough Plaster",
            "suggestion_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/white_rough_plaster/white_rough_plaster_diff_2k.jpg",
            "link": "https://polyhaven.com/a/white_rough_plaster"
        },
        {
            "name": "Velvet Sofa",
            "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/fabric_pattern_07/fabric_pattern_07_col_1_2k.jpg",
            "hex": "#2c5f2d",
            "x": 25,
            "y": 60,
            "suggestion": "Emerald Velvet",
            "suggestion_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/fabric_pattern_05/fabric_pattern_05_col_01_2k.jpg",
            "link": "https://polyhaven.com/a/fabric_pattern_05"
        },
        {
            "name": "Marble Table",
            "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/marble_01/marble_01_diff_2k.jpg",
            "hex": "#f5f5f5",
            "x": 70,
            "y": 65,
            "suggestion": "Carrara Marble",
            "suggestion_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/marble_01/marble_01_diff_2k.jpg",
            "link": "https://polyhaven.com/a/marble_01"
        }
    ]

    reference_textures = []
    if ref_bytes:
        reference_textures = [
            {
                "name": "Warm Walnut",
                "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/walnut_veneer/walnut_veneer_diff_2k.jpg",
                "note": "More pronounced grain, slightly cooler tint",
                "link": "https://polyhaven.com/textures/wood",
                "hex": "#8a6a4f",
                "x": 35,
                "y": 45,
            },
            {
                "name": "Brushed Brass",
                "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/brass_pure/brass_pure_diff_2k.jpg",
                "note": "Use metal/roughness workflow; reduce roughness a bit",
                "link": "https://polyhaven.com/textures/metal",
                "hex": "#c7a24a",
                "x": 65,
                "y": 30,
            },
            {
                "name": "Green Velvet",
                "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/fabric_pattern_05/fabric_pattern_05_col_01_2k.jpg",
                "note": "Rich, deep green fabric for upholstery",
                "link": "https://polyhaven.com/a/fabric_pattern_05",
                "hex": "#1a472a",
                "x": 20,
                "y": 60,
            },
            {
                "name": "White Marble",
                "texture_url": "https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/marble_01/marble_01_diff_2k.jpg",
                "note": "Classic white marble with subtle veining",
                "link": "https://polyhaven.com/a/marble_01",
                "hex": "#eeeeee",
                "x": 75,
                "y": 70,
            }
        ]

    differences = []
    if ref_bytes:
        differences = [
            "Wood grain too smooth compared to reference.",
            "Flooring color slightly warmer than reference.",
            "Metal accents: increase anisotropic highlight to match brushed brass.",
        ]

    return jsonify(
        analysis=analysis,
        analysis_ref=analysis_ref,
        render_textures=render_textures,
        reference_textures=reference_textures,
        differences=differences,
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
