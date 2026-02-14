# AI Background Remover (High Precision & Share)

This project is a Flask-based web application that uses **U2NET** model to remove image backgrounds with high precision.

## Features
- **High Precision:** Uses `u2net` ONNX model for fast and accurate removal.
- **Client-Side Upscale:** Upscales images to 5500x5500 pixels directly in the browser (no server timeout).
- **Share Link:** Upload images to get a shareable link (unlimited size) via Gofile.io.
- **Batch Processing:** Process multiple images at once.
- **Modern UI:** Tailwind CSS, Dark Mode, Arabic/English support.
- **Responsive:** Works on mobile and desktop.

## Deployment (Vercel)
1. Push to GitHub using `git_push.bat`.
2. Import project in Vercel.
3. Deploy! (No special config needed).

**Note:**
- Initial cold start might take a few seconds to download the model (~176MB) to `/tmp`.
- Large files (>4.5MB) are automatically compressed client-side before processing to fit Vercel limits.
- Upscaling happens on your device, saving server resources.
