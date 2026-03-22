#!/usr/bin/env python3
"""
EFTA Verifier — native desktop app for verifying Epstein Files findings.
Renders source PDF pages alongside OCR text for side-by-side comparison.

Usage: python3 app.py
"""

import base64
import glob
import json
import os
import re
import shutil
import tempfile
import zipfile

import webview
import Quartz
from CoreFoundation import CFURLCreateFromFileSystemRepresentation
from pypdf import PdfReader


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PDF_BASE = os.path.expanduser(
    "~/Documents/Epstein Files Transparency Act (H.R.4405)/PDF-dokumenter/"
)
OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")

# ---------------------------------------------------------------------------
# PDF index — built once, scans ALL volumes
# ---------------------------------------------------------------------------

_pdf_index = None  # list of (efta_num, full_path)


def get_pdf_index():
    global _pdf_index
    if _pdf_index is not None:
        return _pdf_index
    entries = []
    for vol_dir in glob.glob(os.path.join(PDF_BASE, "VOL*/IMAGES/0001")):
        for f in os.listdir(vol_dir):
            if f.startswith("EFTA") and f.endswith(".pdf"):
                num = int(f.replace("EFTA", "").replace(".pdf", ""))
                entries.append((num, os.path.join(vol_dir, f)))
    _pdf_index = sorted(entries)
    return _pdf_index


def find_pdf(target):
    """Return (filename, full_path, page_0indexed, total_pages) or 4x None."""
    index = get_pdf_index()
    match = None
    for efta_num, full_path in index:
        if efta_num <= target:
            match = (efta_num, full_path)
        else:
            break
    if match is None:
        return None, None, None, None
    efta_num, full_path = match
    page = target - efta_num
    reader = PdfReader(full_path)
    if page < 0 or page >= len(reader.pages):
        return None, None, None, None
    return os.path.basename(full_path), full_path, page, len(reader.pages)


# ---------------------------------------------------------------------------
# PDF page -> PNG via macOS Quartz
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
# Delta encoding / decoding
# ---------------------------------------------------------------------------


def delta_encode(numbers):
    """Encode sorted EFTA numbers as base + base36 deltas. Returns string."""
    nums = sorted(set(numbers))
    if not nums:
        return ""
    parts = [str(nums[0])]
    for i in range(1, len(nums)):
        delta = nums[i] - nums[i - 1]
        parts.append(base36_encode(delta))
    return ".".join(parts)


def delta_decode(encoded):
    """Decode a delta-encoded string back to EFTA numbers."""
    parts = encoded.strip().split(".")
    if not parts or not parts[0].isdigit():
        return []
    nums = [int(parts[0])]
    for p in parts[1:]:
        p = p.strip()
        if not p:
            continue
        nums.append(nums[-1] + base36_decode(p))
    return nums


def base36_encode(n):
    """Encode a non-negative integer as base36."""
    if n == 0:
        return "0"
    chars = ""
    while n:
        n, r = divmod(n, 36)
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + chars
    return chars


def base36_decode(s):
    """Decode a base36 string to integer."""
    return int(s, 36)


def zip_filename(numbers):
    """Generate delta-encoded ZIP filename."""
    nums = sorted(set(numbers))
    encoded = delta_encode(nums)
    return f"efta-{len(nums)}p-{encoded}.zip"


# ---------------------------------------------------------------------------
# API class exposed to JavaScript
# ---------------------------------------------------------------------------

_results_cache = []
_searched_numbers = []


class Api:
    def search(self, query):
        """Search for EFTA numbers. Supports # prefix for delta-encoded input."""
        global _results_cache, _searched_numbers
        _results_cache.clear()
        _searched_numbers.clear()

        query = query.strip()

        # Delta-decode if starts with #
        if query.startswith("#"):
            numbers = delta_decode(query[1:])
        else:
            raw = re.split(r"[,\s]+", query)
            numbers = []
            for r in raw:
                r = r.strip().replace("EFTA", "").replace("efta", "")
                if r.isdigit():
                    numbers.append(int(r))

        if not numbers:
            return json.dumps([])

        # Deduplicate preserving order
        seen = set()
        unique = []
        for n in numbers:
            if n not in seen:
                seen.add(n)
                unique.append(n)

        _searched_numbers = list(unique)
        results = []
        for efta_num in unique:
            filename, pdf_path, page_idx, total_pages = find_pdf(efta_num)
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

        # Return delta-encoded string alongside results for the status bar
        encoded = delta_encode(_searched_numbers)
        return json.dumps({"results": results, "encoded": encoded})

    def download_zip(self):
        """Package results as ZIP with folder-per-EFTA + manifest."""
        if not _results_cache:
            return json.dumps({"error": "No results to download."})

        encoded = delta_encode(_searched_numbers)
        fname = zip_filename(_searched_numbers)

        tmp = os.path.join(tempfile.gettempdir(), fname)
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for entry in _results_cache:
                folder = entry["efta"]
                zf.writestr(f"{folder}/page.png", entry["png"])
                zf.writestr(f"{folder}/ocr.txt", entry["ocr"])
            zf.writestr("manifest.txt", f"#{encoded}\n")

        window = webview.windows[0]
        dest = window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=fname,
            file_types=("ZIP files (*.zip)",),
        )
        if dest:
            save_path = dest if isinstance(dest, str) else dest[0]
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

.top-row { display: flex; align-items: center; margin-bottom: 20px; }
.top-row h1 { font-size: 20px; font-weight: 600; color: #fff; flex: 1; }
.help-btn {
    width: 28px; height: 28px; border-radius: 50%;
    background: #2a2a2a; border: 1px solid #444; color: #888;
    font-size: 15px; cursor: pointer; display: flex;
    align-items: center; justify-content: center; transition: all 0.15s;
}
.help-btn:hover { background: #3a3a3a; color: #fff; border-color: #666; }

.search-row { display: flex; gap: 8px; margin-bottom: 16px; }
#search-input {
    flex: 1; background: #2a2a2a; border: 1px solid #444; color: #e0e0e0;
    padding: 8px 12px; border-radius: 4px; font-size: 14px; font-family: monospace;
}
#search-input::placeholder { color: #555; }
#search-input:focus { outline: none; border-color: #888; }
.btn {
    background: #333; border: 1px solid #555; color: #e0e0e0;
    padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 13px;
    transition: all 0.15s; white-space: nowrap;
}
.btn:hover { background: #444; color: #fff; }
.btn-zip { background: #2a3a2a; border-color: #4a6a4a; }
.btn-zip:hover { background: #3a4a3a; color: #fff; }
.btn:disabled { opacity: 0.4; cursor: default; }

#status { color: #888; font-size: 12px; margin-bottom: 16px; min-height: 16px;
           font-family: monospace; }

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

/* Help overlay */
.overlay {
    display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.7); z-index: 100;
    align-items: center; justify-content: center;
}
.overlay.open { display: flex; }
.overlay-box {
    background: #222; border: 1px solid #444; border-radius: 8px;
    padding: 24px 28px; max-width: 520px; width: 90%;
    color: #ccc; font-size: 13px; line-height: 1.7;
}
.overlay-box h3 { color: #fff; font-size: 15px; margin-bottom: 12px; }
.overlay-box code {
    background: #1a1a1a; padding: 2px 6px; border-radius: 3px;
    font-family: "SF Mono", "Menlo", monospace; font-size: 12px; color: #aaa;
}
.overlay-box p { margin-bottom: 10px; }
.overlay-box p:last-child { margin-bottom: 0; }
</style>
</head>
<body>

<div class="top-row">
    <h1>EFTA Verifier</h1>
    <button class="help-btn" onclick="toggleHelp()" title="Help">?</button>
</div>

<div class="search-row">
    <input type="text" id="search-input"
           placeholder="EFTA numbers (e.g. 02731139) or paste a share code starting with #"
           autocomplete="off">
    <button class="btn" onclick="doSearch()">Search</button>
    <button class="btn btn-zip" id="zip-btn" onclick="doZip()" disabled>Download ZIP</button>
</div>

<div id="status"></div>
<div id="results"></div>

<div class="overlay" id="help-overlay" onclick="closeHelp(event)">
    <div class="overlay-box" onclick="event.stopPropagation()">
        <h3>How to use</h3>
        <p><strong>Search:</strong> Type one or more EFTA document numbers, separated by commas or spaces:<br>
        <code>02731139, 02731096, 02731114</code><br>
        Each number pulls up the original scanned PDF page alongside the OCR text so you can compare them.</p>
        <p><strong>Share codes:</strong> After each search, a short code appears in the status bar (e.g. <code>#02731053.17.f...</code>). This code is a compact way of storing your exact search. Copy it and send it to someone else &mdash; they paste it into the search box and get the same pages instantly. No need to type out all the EFTA numbers again.</p>
        <p><strong>Download ZIP:</strong> Saves all currently displayed pages as a ZIP file. Each EFTA number gets its own folder with the page image and OCR text. The ZIP also contains the share code so the search can be replayed later.</p>
        <p style="color:#666; font-size:11px; margin-top:14px;">Press Escape or click outside to close.</p>
    </div>
</div>

<script>
document.getElementById('search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doSearch();
});
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') document.getElementById('help-overlay').classList.remove('open');
});

function toggleHelp() {
    document.getElementById('help-overlay').classList.toggle('open');
}
function closeHelp(e) {
    if (e.target === document.getElementById('help-overlay'))
        document.getElementById('help-overlay').classList.remove('open');
}

async function doSearch() {
    const input = document.getElementById('search-input').value.trim();
    if (!input) return;

    const resultsEl = document.getElementById('results');
    const status = document.getElementById('status');
    const zipBtn = document.getElementById('zip-btn');

    resultsEl.innerHTML = '<div class="loading">Rendering PDF pages</div>';
    status.textContent = '';
    zipBtn.disabled = true;

    try {
        const raw = await pywebview.api.search(input);
        const resp = JSON.parse(raw);
        const data = resp.results;
        const encoded = resp.encoded;

        if (!data || !data.length) {
            resultsEl.innerHTML = '<div class="error-msg">No valid EFTA numbers found.</div>';
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
                if (r.ocr_file) html += ' &middot; ' + r.ocr_file;
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

        resultsEl.innerHTML = html;
        status.textContent = data.length + ' result(s)  \u2014  Share code: #' + encoded;
        zipBtn.disabled = imageCount === 0;

    } catch (e) {
        resultsEl.innerHTML = '<div class="error-msg">Error: ' + e + '</div>';
    }
}

async function doZip() {
    const status = document.getElementById('status');
    status.textContent = 'Preparing ZIP...';
    try {
        const raw = await pywebview.api.download_zip();
        const data = JSON.parse(raw);
        if (data.saved) status.textContent = 'Saved: ' + data.saved;
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
