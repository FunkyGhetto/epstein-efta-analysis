#!/usr/bin/env python3
"""
EFTA Verifier — native desktop app for verifying Epstein Files findings.
Renders source PDF pages alongside OCR text for side-by-side comparison.

Usage: python3 app.py
"""

import base64
import glob
import io
import json
import os
import re
import tempfile
import zipfile

import webview
import Quartz
from CoreFoundation import CFURLCreateFromFileSystemRepresentation
from pypdf import PdfReader


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PDF_DIR = os.path.expanduser(
    "~/Documents/Epstein Files Transparency Act (H.R.4405)/"
    "PDF-dokumenter/VOL00012/IMAGES/0001/"
)
OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")

# ---------------------------------------------------------------------------
# PDF index — built once
# ---------------------------------------------------------------------------

_pdf_index = None


def get_pdf_index():
    global _pdf_index
    if _pdf_index is not None:
        return _pdf_index
    entries = []
    for f in os.listdir(PDF_DIR):
        if f.startswith("EFTA") and f.endswith(".pdf"):
            num = int(f.replace("EFTA", "").replace(".pdf", ""))
            entries.append((num, f))
    _pdf_index = sorted(entries)
    return _pdf_index


def find_pdf(target):
    """Return (filename, page_0indexed, total_pages) or (None, None, None)."""
    index = get_pdf_index()
    match = None
    for efta_num, filename in index:
        if efta_num <= target:
            match = (efta_num, filename)
        else:
            break
    if match is None:
        return None, None, None
    efta_num, filename = match
    page = target - efta_num
    reader = PdfReader(os.path.join(PDF_DIR, filename))
    if page < 0 or page >= len(reader.pages):
        return None, None, None
    return filename, page, len(reader.pages)


# ---------------------------------------------------------------------------
# PDF page → PNG via macOS Quartz
# ---------------------------------------------------------------------------


def render_pdf_page_to_png(pdf_path, page_index, dpi=200):
    """Render a single PDF page to PNG bytes using macOS Quartz."""
    url = CFURLCreateFromFileSystemRepresentation(
        None, pdf_path.encode("utf-8"), len(pdf_path.encode("utf-8")), False
    )
    pdf_doc = Quartz.CGPDFDocumentCreateWithURL(url)
    if pdf_doc is None:
        return None

    page = Quartz.CGPDFDocumentGetPage(pdf_doc, page_index + 1)
    if page is None:
        return None

    page_rect = Quartz.CGPDFPageGetBoxRect(page, Quartz.kCGPDFMediaBox)
    scale = dpi / 72.0
    width = int(page_rect.size.width * scale)
    height = int(page_rect.size.height * scale)

    cs = Quartz.CGColorSpaceCreateDeviceRGB()
    ctx = Quartz.CGBitmapContextCreate(
        None, width, height, 8, width * 4, cs,
        Quartz.kCGImageAlphaPremultipliedLast,
    )

    Quartz.CGContextSetRGBFillColor(ctx, 1.0, 1.0, 1.0, 1.0)
    Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, width, height))
    Quartz.CGContextScaleCTM(ctx, scale, scale)
    Quartz.CGContextDrawPDFPage(ctx, page)

    image = Quartz.CGBitmapContextCreateImage(ctx)

    tmp_png = os.path.join(tempfile.gettempdir(), f"efta_render_{os.getpid()}.png")
    tmp_url = CFURLCreateFromFileSystemRepresentation(
        None, tmp_png.encode("utf-8"), len(tmp_png.encode("utf-8")), False
    )
    dest = Quartz.CGImageDestinationCreateWithURL(tmp_url, "public.png", 1, None)
    Quartz.CGImageDestinationAddImage(dest, image, None)
    Quartz.CGImageDestinationFinalize(dest)

    with open(tmp_png, "rb") as f:
        png_bytes = f.read()
    os.unlink(tmp_png)
    return png_bytes


# ---------------------------------------------------------------------------
# OCR text extraction
# ---------------------------------------------------------------------------


def find_ocr_text(efta_num):
    """Find the OCR text block for a given EFTA number from the ocr/ files.

    OCR markers are page footers captured AFTER the page body text.
    The content BETWEEN marker (N-1) and marker N is the body text of page N.
    """
    prev_num = efta_num - 1

    ocr_files = sorted(glob.glob(os.path.join(OCR_DIR, "epstein_ren*.txt")))

    for ocr_path in ocr_files:
        with open(ocr_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        marker_re = re.compile(r"EFTA\d{5,8}")
        positions = [(m.start(), m.end(), int(m.group().replace("EFTA", "")))
                     for m in marker_re.finditer(content)]

        for i, (pos, end_pos, marker_num) in enumerate(positions):
            if marker_num == prev_num:
                start = end_pos
                if i + 1 < len(positions):
                    end = positions[i + 1][0]
                else:
                    end = start + 5000
                end = min(end, start + 5000)
                text = content[start:end].strip()
                return text, os.path.basename(ocr_path)

    return None, None


# ---------------------------------------------------------------------------
# API class exposed to JavaScript
# ---------------------------------------------------------------------------

_results_cache = []


class Api:
    def search(self, query):
        """Search for EFTA numbers. Returns JSON array of results."""
        global _results_cache
        _results_cache.clear()

        raw = re.split(r"[,\s]+", query.strip())
        numbers = []
        for r in raw:
            r = r.strip().replace("EFTA", "").replace("efta", "")
            if r.isdigit():
                numbers.append(int(r))

        if not numbers:
            return json.dumps([])

        seen = set()
        unique = []
        for n in numbers:
            if n not in seen:
                seen.add(n)
                unique.append(n)

        results = []
        for efta_num in unique:
            filename, page_idx, total_pages = find_pdf(efta_num)
            ocr_text, ocr_file = find_ocr_text(efta_num)

            result = {
                "efta": f"EFTA{efta_num:08d}",
                "efta_num": efta_num,
                "pdf": filename,
                "page": page_idx + 1 if page_idx is not None else None,
                "total_pages": total_pages,
                "ocr_text": ocr_text or "No OCR text found.",
                "ocr_file": ocr_file or "",
                "image": None,
                "error": None,
            }

            if filename is None:
                result["error"] = "EFTA number not found in any PDF."
                results.append(result)
                continue

            pdf_path = os.path.join(PDF_DIR, filename)
            png_bytes = render_pdf_page_to_png(pdf_path, page_idx, dpi=200)
            if png_bytes:
                b64 = base64.b64encode(png_bytes).decode("ascii")
                result["image"] = f"data:image/png;base64,{b64}"
                _results_cache.append({
                    "efta": f"EFTA{efta_num:08d}",
                    "png": png_bytes,
                    "ocr": ocr_text or "",
                })

            results.append(result)

        return json.dumps(results)

    def download_zip(self):
        """Package results as ZIP with folder-per-EFTA structure."""
        if not _results_cache:
            return json.dumps({"error": "No results to download."})

        tmp = os.path.join(tempfile.gettempdir(), "efta-verification.zip")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for entry in _results_cache:
                folder = entry["efta"]
                zf.writestr(f"{folder}/page.png", entry["png"])
                zf.writestr(f"{folder}/ocr.txt", entry["ocr"])

        window = webview.windows[0]
        dest = window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename="efta-verification.zip",
            file_types=("ZIP files (*.zip)",),
        )
        if dest:
            save_path = dest if isinstance(dest, str) else dest[0]
            import shutil
            shutil.copy2(tmp, save_path)
            os.unlink(tmp)
            return json.dumps({"saved": save_path})

        os.unlink(tmp)
        return json.dumps({"cancelled": True})


# ---------------------------------------------------------------------------
# HTML / CSS / JS
# ---------------------------------------------------------------------------

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: #1a1a1a; color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 14px; padding: 24px; overflow-y: auto;
}
h1 { font-size: 20px; font-weight: 600; margin-bottom: 4px; color: #fff; }
.subtitle { color: #888; font-size: 12px; margin-bottom: 20px; }

.search-row { display: flex; gap: 8px; margin-bottom: 16px; }
#search-input {
    flex: 1; background: #2a2a2a; border: 1px solid #444; color: #e0e0e0;
    padding: 8px 12px; border-radius: 4px; font-size: 14px; font-family: monospace;
}
#search-input::placeholder { color: #666; }
#search-input:focus { outline: none; border-color: #888; }
.btn {
    background: #333; border: 1px solid #555; color: #e0e0e0;
    padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 13px;
    transition: all 0.15s;
}
.btn:hover { background: #444; color: #fff; }
.btn-zip { background: #2a3a2a; border-color: #4a6a4a; }
.btn-zip:hover { background: #3a4a3a; color: #fff; }
.btn:disabled { opacity: 0.4; cursor: default; }

#status { color: #888; font-size: 12px; margin-bottom: 16px; min-height: 16px; }

.result {
    background: #222; border: 1px solid #333; border-radius: 6px;
    margin-bottom: 20px; overflow: hidden;
}
.result-header {
    background: #2a2a2a; padding: 12px 16px; border-bottom: 1px solid #333;
    display: flex; justify-content: space-between; align-items: center;
}
.result-header h2 { font-size: 16px; color: #fff; font-family: monospace; }
.result-meta { color: #888; font-size: 12px; font-family: monospace; }
.result-body { display: flex; }
.result-image {
    flex: 1; min-width: 0; padding: 12px; border-right: 1px solid #333;
    display: flex; align-items: flex-start; justify-content: center;
    background: #1a1a1a;
}
.result-image img {
    max-width: 100%; height: auto; border: 1px solid #333; border-radius: 2px;
}
.result-ocr {
    flex: 1; min-width: 0; padding: 12px; overflow: auto; max-height: 800px;
}
.result-ocr-label { color: #888; font-size: 11px; margin-bottom: 6px; }
.result-ocr pre {
    background: #1a1a1a; border: 1px solid #333; border-radius: 4px;
    padding: 12px; font-family: "SF Mono", "Menlo", "Monaco", monospace;
    font-size: 12px; line-height: 1.5; color: #ccc;
    white-space: pre-wrap; word-wrap: break-word;
}
.error-msg { color: #e55; padding: 16px; }
.loading { text-align: center; padding: 40px; color: #888; }
.loading::after {
    content: ""; display: inline-block; width: 20px; height: 20px;
    border: 2px solid #444; border-top-color: #aaa; border-radius: 50%;
    animation: spin 0.8s linear infinite; margin-left: 10px; vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>

<h1>EFTA Verifier</h1>
<div class="subtitle">PDF page + OCR text side by side</div>

<div class="search-row">
    <input type="text" id="search-input"
           placeholder="Enter EFTA numbers (e.g. 02731139, 02731096)"
           autocomplete="off">
    <button class="btn" onclick="doSearch()">Search</button>
    <button class="btn btn-zip" id="zip-btn" onclick="doZip()" disabled>Download ZIP</button>
</div>

<div id="status"></div>
<div id="results"></div>

<script>
document.getElementById('search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doSearch();
});

async function doSearch() {
    const input = document.getElementById('search-input').value.trim();
    if (!input) return;

    const results = document.getElementById('results');
    const status = document.getElementById('status');
    const zipBtn = document.getElementById('zip-btn');

    results.innerHTML = '<div class="loading">Rendering PDF pages</div>';
    status.textContent = '';
    zipBtn.disabled = true;

    try {
        const raw = await pywebview.api.search(input);
        const data = JSON.parse(raw);

        if (!data.length) {
            results.innerHTML = '<div class="error-msg">No valid EFTA numbers found.</div>';
            return;
        }

        let html = '';
        let imageCount = 0;
        data.forEach(r => {
            html += '<div class="result">';
            html += '<div class="result-header">';
            html += '<h2>' + r.efta + '</h2>';
            if (r.pdf) {
                html += '<span class="result-meta">' + r.pdf + ' p.' + r.page + '/' + r.total_pages;
                if (r.ocr_file) html += ' · OCR: ' + r.ocr_file;
                html += '</span>';
            }
            html += '</div>';

            if (r.error) {
                html += '<div class="error-msg">' + r.error + '</div>';
            } else {
                html += '<div class="result-body">';
                html += '<div class="result-image">';
                if (r.image) {
                    html += '<img src="' + r.image + '" alt="' + r.efta + '">';
                    imageCount++;
                } else {
                    html += '<div class="error-msg">Failed to render page.</div>';
                }
                html += '</div>';
                html += '<div class="result-ocr">';
                html += '<div class="result-ocr-label">OCR TEXT</div>';
                html += '<pre>' + escapeHtml(r.ocr_text) + '</pre>';
                html += '</div>';
                html += '</div>';
            }
            html += '</div>';
        });

        results.innerHTML = html;
        status.textContent = data.length + ' result(s)';
        zipBtn.disabled = imageCount === 0;

    } catch (e) {
        results.innerHTML = '<div class="error-msg">Error: ' + e + '</div>';
    }
}

async function doZip() {
    const status = document.getElementById('status');
    status.textContent = 'Preparing ZIP...';
    try {
        const raw = await pywebview.api.download_zip();
        const data = JSON.parse(raw);
        if (data.saved) status.textContent = 'Saved to ' + data.saved;
        else if (data.cancelled) status.textContent = 'Cancelled.';
        else if (data.error) status.textContent = data.error;
    } catch (e) {
        status.textContent = 'Error: ' + e;
    }
}

function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api = Api()
    webview.create_window(
        "EFTA Verifier",
        html=HTML,
        js_api=api,
        width=1400,
        height=900,
        min_size=(900, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
