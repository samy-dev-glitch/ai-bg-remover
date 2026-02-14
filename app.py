import os
import io
import numpy as np
import onnxruntime as ort
from flask import Flask, request, send_file, render_template, jsonify
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import urllib.request

app = Flask(__name__)

# --- Model Configuration ---
MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
MODEL_PATH = "/tmp/u2net.onnx" # Writable path in Vercel

def load_session():
    # Check if model exists, if not download it
    if not os.path.exists(MODEL_PATH):
        print("Downloading u2net model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")
    
    # Create ONNX session
    return ort.InferenceSession(MODEL_PATH)

def enhance_image(image_pil):
    """
    Apply advanced image enhancement using Pillow (Lightweight):
    1. Detail Enhancement
    2. Unsharp Mask (Sharpening)
    3. Contrast Enhancement
    """
    # Ensure RGB
    if image_pil.mode == 'RGBA':
        r, g, b, a = image_pil.split()
        rgb_image = Image.merge('RGB', (r, g, b))
    else:
        rgb_image = image_pil.convert("RGB")
        a = None

    # 1. Detail Enhancement (Skipped for performance)
    # enhanced = rgb_image.filter(ImageFilter.DETAIL)
    enhanced = rgb_image
    
    # 2. Sharpening (Moderate)
    enhancer_sharpness = ImageEnhance.Sharpness(enhanced)
    enhanced = enhancer_sharpness.enhance(1.3) # 30% Sharpness is safer and faster
    
    # 3. Contrast (Auto Contrast with less cutoff)
    enhanced = ImageOps.autocontrast(enhanced, cutoff=0.5)
    
    # Recombine Alpha if exists
    if a is not None:
        enhanced = enhanced.convert("RGBA")
        enhanced.putalpha(a)
        
    return enhanced

# Global session variable (Lazy loaded)
session = None

def preprocess(image):
    # Resize to 320x320 (standard for u2net)
    img = image.resize((320, 320), Image.Resampling.LANCZOS)
    img_np = np.array(img).astype(np.float32)
    
    # Normalize
    img_np /= 255.0
    img_np -= [0.485, 0.456, 0.406]
    img_np /= [0.229, 0.224, 0.225]
    
    # Transpose to (1, 3, 320, 320)
    img_np = img_np.transpose((2, 0, 1))
    img_np = np.expand_dims(img_np, axis=0)
    
    return img_np

def postprocess(pred, original_image):
    # Pred is (1, 1, 320, 320)
    ma = np.squeeze(pred)
    ma = (ma - ma.min()) / (ma.max() - ma.min())
    
    # Resize mask to original size
    ma = Image.fromarray((ma * 255).astype(np.uint8)).resize(original_image.size, Image.Resampling.LANCZOS)
    
    # Apply mask
    empty = Image.new("RGBA", original_image.size, 0)
    final = Image.composite(original_image, empty, ma)
    return final

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    global session
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Initialize session if needed
        if session is None:
            session = load_session()

        input_data = file.read()
        original_image = Image.open(io.BytesIO(input_data)).convert("RGB")
        
        # Check options
        should_remove_bg = request.form.get('remove_bg') == 'true'
        should_upscale = request.form.get('upscale') == 'true'
        should_enhance = request.form.get('enhance') == 'true'
        
        if should_remove_bg:
            # Preprocess
            input_tensor = preprocess(original_image)
            
            # Inference
            input_name = session.get_inputs()[0].name
            output_name = session.get_outputs()[0].name
            result = session.run([output_name], {input_name: input_tensor})
            
            # Postprocess
            final_image = postprocess(result[0], original_image.convert("RGBA"))
        else:
            # Just use original image
            final_image = original_image.convert("RGBA")
        
        if should_enhance:
            # Apply Pillow enhancement (Denoise, Sharpen, Contrast)
            final_image = enhance_image(final_image)

        # Server-side upscale is REMOVED to prevent timeouts/memory errors on Vercel.
        # Upscaling to 5500x5500 is now handled client-side in the browser.
        final_to_save = final_image
        
        # Save (Optimize=False for speed)
        img_io = io.BytesIO()
        final_to_save.save(img_io, 'PNG', optimize=False)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f"processed_{file.filename}")

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from waitress import serve
    print("Starting server...")
    serve(app, host="0.0.0.0", port=5000)
