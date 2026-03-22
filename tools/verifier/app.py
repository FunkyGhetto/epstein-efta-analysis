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
from pypdf import PdfReader, PdfWriter


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PDF_DIR = os.path.expanduser(
    "~/Documents/Epstein Files Transparency Act (H.R.4405)/"
    "PDF-dokumenter/VOL00012/IMAGES/0001/"
)
OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")

# ---------------------------------------------------------------------------
# Quick-verify presets
# ---------------------------------------------------------------------------

PRESETS = [
    ("Dubin", "02731139"),
    ("Weinstein", "02731096"),
    ("Black HT", "02731477"),
    ("Coop. Defendants", "02731053"),
    ("No cameras", "02731148"),
    ("No client accounts", "02731148"),
    ("Indyke police", "02731123"),
    ("Indyke prison", "02731127"),
    ("Blaine", "02731111"),
    ("Wexner wealth", "02731146"),
    ("Staley", "02731114"),
    ("Black massage", "02731114"),
    ("Black HT chain", "02731638"),
    ("Groff Dec 2018", "02731133"),
]

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

    # Quartz pages are 1-indexed
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

    # White background
    Quartz.CGContextSetRGBFillColor(ctx, 1.0, 1.0, 1.0, 1.0)
    Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, width, height))

    Quartz.CGContextScaleCTM(ctx, scale, scale)
    Quartz.CGContextDrawPDFPage(ctx, page)

    image = Quartz.CGBitmapContextCreateImage(ctx)

    # Write PNG to temp file and read back as bytes
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
    So the marker EFTA02731138 appears at the end of page 02731138's text,
    meaning the content BETWEEN marker (N-1) and marker N is the actual
    body text of page N.  To get text for page 02731139, we find the
    EFTA02731138 marker and return everything from there up to EFTA02731139.
    """
    prev_num = efta_num - 1  # the marker that precedes our page's content

    ocr_files = sorted(glob.glob(os.path.join(OCR_DIR, "epstein_ren*.txt")))

    for ocr_path in ocr_files:
        with open(ocr_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        marker_re = re.compile(r"EFTA\d{5,8}")
        positions = [(m.start(), m.end(), int(m.group().replace("EFTA", "")))
                     for m in marker_re.finditer(content)]

        for i, (pos, end_pos, marker_num) in enumerate(positions):
            if marker_num == prev_num:
                # Start of our page's text is right after the (N-1) marker
                start = end_pos
                # End is at the N marker (our EFTA number) or +5000
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

# Store rendered images for ZIP download
_rendered_images = {}


class Api:
    def search(self, query):
        """Search for EFTA numbers. Returns JSON array of results."""
        global _rendered_images
        _rendered_images.clear()

        # Parse comma/space separated numbers
        raw = re.split(r"[,\s]+", query.strip())
        numbers = []
        for r in raw:
            r = r.strip().replace("EFTA", "").replace("efta", "")
            if r.isdigit():
                numbers.append(int(r))

        if not numbers:
            return json.dumps([])

        # Deduplicate while preserving order
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
                "ocr_file": ocr_file or "—",
                "image": None,
                "error": None,
            }

            if filename is None:
                result["error"] = "EFTA number not found in any PDF."
                results.append(result)
                continue

            # Render page
            pdf_path = os.path.join(PDF_DIR, filename)
            png_bytes = render_pdf_page_to_png(pdf_path, page_idx, dpi=200)
            if png_bytes:
                b64 = base64.b64encode(png_bytes).decode("ascii")
                result["image"] = f"data:image/png;base64,{b64}"
                _rendered_images[f"EFTA{efta_num:08d}.png"] = png_bytes

            results.append(result)

        return json.dumps(results)

    def download_zip(self):
        """Package all rendered images as a ZIP, prompt save dialog."""
        if not _rendered_images:
            return json.dumps({"error": "No images to download."})

        # Build ZIP in memory, write to temp file
        tmp = os.path.join(tempfile.gettempdir(), "efta-verification.zip")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, data in _rendered_images.items():
                zf.writestr(name, data)

        # Use pywebview save dialog
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
    font-size: 14px; padding: 20px; overflow-y: auto;
}
h1 { font-size: 20px; font-weight: 600; margin-bottom: 6px; color: #fff; }
.subtitle { color: #888; font-size: 12px; margin-bottom: 18px; }

/* Preset buttons */
.presets { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
.preset-btn {
    background: #2a2a2a; border: 1px solid #444; color: #ccc;
    padding: 5px 10px; border-radius: 4px; cursor: pointer;
    font-size: 12px; transition: all 0.15s;
}
.preset-btn:hover { background: #3a3a3a; color: #fff; border-color: #666; }

/* Search bar */
.search-row { display: flex; gap: 8px; margin-bottom: 16px; }
#search-input {
    flex: 1; background: #2a2a2a; border: 1px solid #444; color: #e0e0e0;
    padding: 8px 12px; border-radius: 4px; font-size: 14px; font-family: monospace;
}
#search-input::placeholder { color: #666; }
#search-input:focus { outline: none; border-color: #888; }
.search-btn, .zip-btn {
    background: #333; border: 1px solid #555; color: #e0e0e0;
    padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 13px;
    transition: all 0.15s;
}
.search-btn:hover { background: #444; color: #fff; }
.zip-btn { background: #2a3a2a; border-color: #4a6a4a; }
.zip-btn:hover { background: #3a4a3a; color: #fff; }
.zip-btn:disabled { opacity: 0.4; cursor: default; }

/* Status */
#status { color: #888; font-size: 12px; margin-bottom: 16px; min-height: 16px; }

/* Results */
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
.result-body { display: flex; gap: 0; }
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

/* Loading spinner */
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
<div class="subtitle">PDF page + OCR text side by side &mdash; verify any finding from the analysis</div>

<div class="presets" id="presets"></div>

<div class="search-row">
    <input type="text" id="search-input"
           placeholder="Enter EFTA numbers (e.g. 02731113, 02731096)"
           autocomplete="off">
    <button class="search-btn" onclick="doSearch()">Search</button>
    <button class="zip-btn" id="zip-btn" onclick="doZip()" disabled>Download ZIP</button>
</div>

<div id="status"></div>
<div id="results"></div>

<script>
const PRESETS = PRESET_DATA;

// Build preset buttons
const presetsEl = document.getElementById('presets');
PRESETS.forEach(([label, num]) => {
    const btn = document.createElement('button');
    btn.className = 'preset-btn';
    btn.textContent = label + ' (' + num + ')';
    btn.onclick = () => {
        document.getElementById('search-input').value = num;
        doSearch();
    };
    presetsEl.appendChild(btn);
});

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
                html += '<span class="result-meta">' + r.pdf + ' &mdash; page ' + r.page + '/' + r.total_pages + ' &mdash; OCR: ' + r.ocr_file + '</span>';
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
                html += '<div class="result-ocr-label">OCR TEXT (' + r.ocr_file + ')</div>';
                html += '<pre>' + escapeHtml(r.ocr_text) + '</pre>';
                html += '</div>';
                html += '</div>';
            }
            html += '</div>';
        });

        results.innerHTML = html;
        status.textContent = data.length + ' result(s) rendered.';
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
        if (data.saved) {
            status.textContent = 'Saved to ' + data.saved;
        } else if (data.cancelled) {
            status.textContent = 'Download cancelled.';
        } else if (data.error) {
            status.textContent = data.error;
        }
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
""".replace(
    "PRESET_DATA",
    json.dumps([[label, num] for label, num in PRESETS]),
)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api = Api()
    window = webview.create_window(
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
