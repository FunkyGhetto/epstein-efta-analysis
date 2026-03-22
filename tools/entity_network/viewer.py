#!/usr/bin/env python3
"""
Entity Network Viewer — browse extracted names, connections, and flagged entities.
Reads from entities.json, cooccurrence.json, and flagged.json.

Usage: python3 viewer.py
"""

import json
import os
import re
import tempfile
from collections import defaultdict

import webview

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(name):
    # Check root dir first, then data/ subfolder
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        path = os.path.join(DATA_DIR, "data", name)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


ENTITIES = load_json("entities.json")
COOCCURRENCE = load_json("cooccurrence.json")
FLAGGED = load_json("flagged.json") if os.path.exists(os.path.join(DATA_DIR, "flagged.json")) else []

# Pre-build connection index: name → [(other_name, count, pages), ...]
CONNECTIONS = defaultdict(list)
for key, data in COOCCURRENCE.items():
    a, b = data["name_a"], data["name_b"]
    CONNECTIONS[a].append((b, data["count"], data["pages"]))
    CONNECTIONS[b].append((a, data["count"], data["pages"]))

# Sort connections by count descending
for name in CONNECTIONS:
    CONNECTIONS[name].sort(key=lambda x: -x[1])


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


class Api:
    def get_names(self):
        """Return all names sorted by occurrence count."""
        names = []
        for name, data in ENTITIES.items():
            names.append({"name": name, "count": data["count"]})
        names.sort(key=lambda x: -x["count"])
        return json.dumps(names)

    def get_entity(self, name):
        """Return full entity data + connections."""
        if name not in ENTITIES:
            return json.dumps(None)
        ent = ENTITIES[name]
        conns = CONNECTIONS.get(name, [])[:30]
        return json.dumps({
            "name": name,
            "count": ent["count"],
            "occurrences": ent["occurrences"][:200],
            "connections": [{"name": c[0], "count": c[1], "pages": c[2][:10]} for c in conns],
        })

    def get_flagged(self):
        """Return flagged names."""
        return json.dumps(FLAGGED[:100])

    def search_names(self, query):
        """Filter names by substring."""
        q = query.lower()
        matches = []
        for name, data in ENTITIES.items():
            if q in name.lower():
                matches.append({"name": name, "count": data["count"]})
        matches.sort(key=lambda x: -x["count"])
        return json.dumps(matches[:100])

    def export_dossier(self, name):
        """Export a person's dossier as a text file via save dialog."""
        if name not in ENTITIES:
            return json.dumps({"error": "Name not found"})

        ent = ENTITIES[name]
        conns = CONNECTIONS.get(name, [])

        lines = [f"DOSSIER: {name}", f"Total occurrences: {ent['count']}", ""]

        # Flagged keywords
        for f in FLAGGED:
            if f["name"] == name:
                lines.append(f"Keyword score: {f['total_score']}")
                for kw, cnt in sorted(f["keyword_breakdown"].items(), key=lambda x: -x[1]):
                    lines.append(f"  {kw}: {cnt}")
                lines.append("")
                break

        lines.append("CONNECTIONS:")
        for other, count, pages in conns[:30]:
            lines.append(f"  {other}: {count} shared pages")
        lines.append("")

        lines.append("OCCURRENCES:")
        for occ in ent["occurrences"]:
            efta = f"EFTA{occ['efta_page']:08d}" if occ.get("efta_page") else "unknown"
            lines.append(f"  [{efta}] {occ['file']}:{occ['line']}")
            lines.append(f"    {occ['context'][:200]}")
            lines.append("")

        text = "\n".join(lines)

        tmp = os.path.join(tempfile.gettempdir(), f"dossier-{name.replace(' ', '_')}.txt")
        with open(tmp, "w") as f:
            f.write(text)

        window = webview.windows[0]
        dest = window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=f"dossier-{name.replace(' ', '_')}.txt",
            file_types=("Text files (*.txt)",),
        )
        if dest:
            import shutil
            save_path = dest if isinstance(dest, str) else dest[0]
            shutil.copy2(tmp, save_path)
            os.unlink(tmp)
            return json.dumps({"saved": save_path})

        os.unlink(tmp)
        return json.dumps({"cancelled": True})

    def export_all(self):
        """Export all data as a ZIP: entities, cooccurrence, flagged JSONs + all dossiers."""
        import shutil
        import zipfile

        tmp = os.path.join(tempfile.gettempdir(), "efta-entity-network.zip")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            # Raw JSON data
            for name in ["entities.json", "cooccurrence.json", "flagged.json"]:
                path = os.path.join(DATA_DIR, name)
                if os.path.exists(path):
                    zf.write(path, f"data/{name}")

            # Top 50 flagged dossiers as text files
            flagged_names = [f["name"] for f in FLAGGED[:50]]
            for pname in flagged_names:
                if pname not in ENTITIES:
                    continue
                ent = ENTITIES[pname]
                conns = CONNECTIONS.get(pname, [])
                lines = [f"DOSSIER: {pname}", f"Total occurrences: {ent['count']}", ""]
                for f in FLAGGED:
                    if f["name"] == pname:
                        lines.append(f"Keyword score: {f['total_score']}")
                        for kw, cnt in sorted(f["keyword_breakdown"].items(), key=lambda x: -x[1]):
                            lines.append(f"  {kw}: {cnt}")
                        lines.append("")
                        break
                lines.append("CONNECTIONS:")
                for other, count, pages in conns[:30]:
                    lines.append(f"  {other}: {count} shared pages")
                lines.append("")
                lines.append("OCCURRENCES:")
                for occ in ent["occurrences"]:
                    efta = f"EFTA{occ['efta_page']:08d}" if occ.get("efta_page") else "unknown"
                    lines.append(f"  [{efta}] {occ['file']}:{occ['line']}")
                    lines.append(f"    {occ['context'][:200]}")
                    lines.append("")
                safe = pname.replace(" ", "_").replace("/", "_")
                zf.writestr(f"dossiers/{safe}.txt", "\n".join(lines))

            # Summary
            summary = [
                "EFTA Entity Network — Export Summary",
                f"Total unique names: {len(ENTITIES)}",
                f"Co-occurrence pairs: {len(COOCCURRENCE)}",
                f"Flagged names: {len(FLAGGED)}",
                f"Dossiers included: {len(flagged_names)} (top 50 by keyword score)",
                "",
                "TOP 20 FLAGGED:",
            ]
            for f in FLAGGED[:20]:
                summary.append(f"  {f['name']}: score={f['total_score']} ({f['occurrence_count']} occ)")
            zf.writestr("summary.txt", "\n".join(summary))

        window = webview.windows[0]
        dest = window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename="efta-entity-network.zip",
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
# HTML
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
    font-size: 13px; display: flex; height: 100vh; overflow: hidden;
}

/* Tabs + sidebar */
.sidebar {
    width: 320px; min-width: 320px; background: #222;
    border-right: 1px solid #333; display: flex; flex-direction: column;
}
.tabs {
    display: flex; border-bottom: 1px solid #333; background: #2a2a2a;
}
.tab {
    flex: 1; padding: 10px 8px; text-align: center; cursor: pointer;
    color: #888; font-size: 12px; border-bottom: 2px solid transparent;
    transition: all 0.15s;
}
.tab:hover { color: #ccc; }
.tab.active { color: #fff; border-bottom-color: #888; }
.search-box {
    padding: 8px; border-bottom: 1px solid #333;
}
.search-box input {
    width: 100%; background: #1a1a1a; border: 1px solid #444; color: #e0e0e0;
    padding: 6px 10px; border-radius: 4px; font-size: 13px;
}
.search-box input::placeholder { color: #555; }
.search-box input:focus { outline: none; border-color: #888; }
.name-list {
    flex: 1; overflow-y: auto; padding: 4px 0;
}
.name-item {
    padding: 6px 12px; cursor: pointer; display: flex;
    justify-content: space-between; transition: background 0.1s;
}
.name-item:hover { background: #2a2a2a; }
.name-item.active { background: #333; }
.name-item .n { color: #e0e0e0; font-size: 13px; }
.name-item .c { color: #666; font-size: 11px; font-family: monospace; }

/* Flagged items */
.flag-item {
    padding: 6px 12px; cursor: pointer; display: flex;
    justify-content: space-between; align-items: center; transition: background 0.1s;
}
.flag-item:hover { background: #2a2a2a; }
.flag-score {
    background: #3a2020; color: #e88; padding: 2px 6px;
    border-radius: 3px; font-size: 11px; font-family: monospace;
}

/* Main content */
.main {
    flex: 1; overflow-y: auto; padding: 24px;
}
.main h2 { font-size: 18px; color: #fff; margin-bottom: 4px; }
.main .subtitle { color: #888; font-size: 12px; margin-bottom: 16px; }
.section-title {
    color: #aaa; font-size: 11px; text-transform: uppercase;
    letter-spacing: 1px; margin: 20px 0 8px 0; padding-bottom: 4px;
    border-bottom: 1px solid #333;
}
.conn-item {
    display: inline-block; background: #2a2a2a; border: 1px solid #333;
    border-radius: 4px; padding: 4px 10px; margin: 2px 4px 2px 0;
    font-size: 12px; cursor: pointer; transition: all 0.15s;
}
.conn-item:hover { background: #333; border-color: #555; color: #fff; }
.conn-count { color: #666; font-size: 11px; }
.occ-item {
    background: #222; border: 1px solid #333; border-radius: 4px;
    padding: 10px 12px; margin-bottom: 8px;
}
.occ-meta { color: #888; font-size: 11px; font-family: monospace; margin-bottom: 4px; }
.occ-ctx {
    font-family: "SF Mono", "Menlo", monospace; font-size: 12px;
    line-height: 1.5; color: #ccc;
}
.export-btn {
    background: #2a3a2a; border: 1px solid #4a6a4a; color: #ccc;
    padding: 6px 14px; border-radius: 4px; cursor: pointer;
    font-size: 12px; margin-left: 12px; transition: all 0.15s;
}
.export-btn:hover { background: #3a4a3a; color: #fff; }
.kw-tag {
    display: inline-block; background: #3a2020; border: 1px solid #5a3030;
    border-radius: 3px; padding: 2px 6px; margin: 2px; font-size: 11px; color: #e88;
}
.placeholder {
    color: #555; text-align: center; padding: 60px 20px; font-size: 14px;
}
</style>
</head>
<body>

<div class="sidebar">
    <div class="tabs">
        <div class="tab active" id="tab-names" onclick="switchTab('names')">Names</div>
        <div class="tab" id="tab-flagged" onclick="switchTab('flagged')">Flagged</div>
    </div>
    <div class="search-box">
        <input type="text" id="search" placeholder="Filter names..." oninput="filterNames()">
    </div>
    <div class="name-list" id="name-list"></div>
    <div style="padding:8px;border-top:1px solid #333;">
        <button class="export-btn" style="width:100%;margin:0;" onclick="exportAll()">Download All Data (ZIP)</button>
    </div>
</div>

<div class="main" id="main">
    <div class="placeholder">Select a name from the list to view their profile.</div>
</div>

<script>
let currentTab = 'names';
let allNames = [];
let allFlagged = [];

async function init() {
    const raw = await pywebview.api.get_names();
    allNames = JSON.parse(raw);
    renderNameList(allNames);

    const fraw = await pywebview.api.get_flagged();
    allFlagged = JSON.parse(fraw);
}

function switchTab(tab) {
    currentTab = tab;
    document.getElementById('tab-names').classList.toggle('active', tab === 'names');
    document.getElementById('tab-flagged').classList.toggle('active', tab === 'flagged');

    if (tab === 'names') {
        renderNameList(allNames);
    } else {
        renderFlaggedList();
    }
}

function renderNameList(names) {
    const el = document.getElementById('name-list');
    el.innerHTML = names.map(n =>
        '<div class="name-item" onclick="selectName(\\''+esc(n.name)+'\\')"><span class="n">'+esc(n.name)+'</span><span class="c">'+n.count+'</span></div>'
    ).join('');
}

function renderFlaggedList() {
    const el = document.getElementById('name-list');
    el.innerHTML = allFlagged.map(f =>
        '<div class="flag-item" onclick="selectName(\\''+esc(f.name)+'\\')"><span class="n">'+esc(f.name)+'</span><span class="flag-score">'+f.total_score+'</span></div>'
    ).join('');
}

async function filterNames() {
    const q = document.getElementById('search').value.trim();
    if (currentTab === 'flagged') {
        if (!q) { renderFlaggedList(); return; }
        const filtered = allFlagged.filter(f => f.name.toLowerCase().includes(q.toLowerCase()));
        const el = document.getElementById('name-list');
        el.innerHTML = filtered.map(f =>
            '<div class="flag-item" onclick="selectName(\\''+esc(f.name)+'\\')"><span class="n">'+esc(f.name)+'</span><span class="flag-score">'+f.total_score+'</span></div>'
        ).join('');
        return;
    }
    if (!q) { renderNameList(allNames); return; }
    const raw = await pywebview.api.search_names(q);
    const names = JSON.parse(raw);
    renderNameList(names);
}

async function selectName(name) {
    const raw = await pywebview.api.get_entity(name);
    const data = JSON.parse(raw);
    if (!data) { return; }

    const main = document.getElementById('main');
    let html = '<div style="display:flex;align-items:center;margin-bottom:4px;">';
    html += '<h2>' + esc(data.name) + '</h2>';
    html += '<button class="export-btn" onclick="exportDossier(\\''+esc(data.name)+'\\')">Export dossier</button>';
    html += '</div>';
    html += '<div class="subtitle">' + data.count + ' occurrences across OCR files</div>';

    // Keyword tags if flagged
    const flagEntry = allFlagged.find(f => f.name === data.name);
    if (flagEntry) {
        html += '<div style="margin-bottom:12px;">';
        for (const [kw, cnt] of Object.entries(flagEntry.keyword_breakdown).sort((a,b) => b[1]-a[1])) {
            html += '<span class="kw-tag">' + esc(kw) + ': ' + cnt + '</span>';
        }
        html += '</div>';
    }

    // Connections
    if (data.connections.length > 0) {
        html += '<div class="section-title">Connections (' + data.connections.length + ')</div>';
        html += '<div style="margin-bottom:12px;">';
        for (const c of data.connections) {
            html += '<span class="conn-item" onclick="selectName(\\''+esc(c.name)+'\\')">'+esc(c.name)+' <span class="conn-count">'+c.count+'</span></span>';
        }
        html += '</div>';
    }

    // Occurrences
    html += '<div class="section-title">Occurrences (showing ' + Math.min(data.occurrences.length, 200) + ')</div>';
    for (const occ of data.occurrences) {
        const efta = occ.efta_page ? 'EFTA' + String(occ.efta_page).padStart(8, '0') : 'unknown';
        html += '<div class="occ-item">';
        html += '<div class="occ-meta">' + efta + ' &middot; ' + esc(occ.file) + ':' + occ.line + '</div>';
        html += '<div class="occ-ctx">' + esc(occ.context) + '</div>';
        html += '</div>';
    }

    main.innerHTML = html;
}

async function exportAll() {
    const main = document.getElementById('main');
    main.innerHTML = '<div class="placeholder">Packaging all data...</div>';
    try {
        const raw = await pywebview.api.export_all();
        const data = JSON.parse(raw);
        if (data.saved) main.innerHTML = '<div class="placeholder">Saved to ' + esc(data.saved) + '</div>';
        else if (data.cancelled) main.innerHTML = '<div class="placeholder">Cancelled.</div>';
    } catch(e) {
        main.innerHTML = '<div class="placeholder">Error: ' + e + '</div>';
    }
}

async function exportDossier(name) {
    const raw = await pywebview.api.export_dossier(name);
    const data = JSON.parse(raw);
    if (data.saved) alert('Saved to ' + data.saved);
}

function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML.replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
}

window.addEventListener('pywebviewready', init);
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
        "EFTA Entity Network",
        html=HTML,
        js_api=api,
        width=1400,
        height=900,
        min_size=(900, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
