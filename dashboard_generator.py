import json
import os
from datetime import datetime

CONTENT_LOG = "content_log.json"

def load_log():
    if os.path.exists(CONTENT_LOG):
        with open(CONTENT_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_to_log(content, shopify_url=""):
    log = load_log()
    entry = {
        "id": len(log) + 1,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "topic": content["topic"],
        "keywords": content.get("keywords", ""),
        "shopify_url": shopify_url,
        "status": {
            "shopify": True if shopify_url else False,
            "twitter": False,
            "threads": False,
            "reddit": False,
            "medium": False
        },
        "content": {
            "blog": content["blog"],
            "twitter": content["twitter"],
            "threads": content["threads"],
            "reddit": content["reddit"],
            "medium": content["medium"]
        }
    }
    log.append(entry)
    with open(CONTENT_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"Saved to content log (entry #{entry['id']})")
    return log

def make_tab_button(entry_id, platform):
    return (
        '<button onclick="showTab(' + str(entry_id) + ', \'' + platform + '\')" '
        'id="btn-' + str(entry_id) + '-' + platform + '" '
        'style="background:#222;color:#ccc;border:1px solid #333;padding:6px 14px;'
        'border-radius:6px;cursor:pointer;font-size:13px;">'
        + platform.title() +
        '</button>'
    )

def make_tab_content(entry_id, platform, text):
    escaped = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return (
        '<div class="tab-content" id="tab-' + str(entry_id) + '-' + platform + '" style="display:none;">'
        '<div style="position:relative;">'
        '<button onclick="copyText(\'content-' + str(entry_id) + '-' + platform + '\')" '
        'style="position:absolute;top:0;right:0;background:#f5c518;border:none;'
        'padding:6px 14px;border-radius:6px;cursor:pointer;font-weight:bold;">Copy</button>'
        '<pre id="content-' + str(entry_id) + '-' + platform + '" '
        'style="white-space:pre-wrap;background:#1a1a1a;color:#eee;'
        'padding:16px;border-radius:8px;font-size:13px;line-height:1.6;padding-right:80px;">'
        + escaped +
        '</pre>'
        '</div>'
        '</div>'
    )

def make_badge(label, done):
    color = "#00c853" if done else "#444"
    return (
        '<span style="background:' + color + ';color:white;padding:3px 10px;'
        'border-radius:20px;font-size:12px;margin-right:6px;">' + label + '</span>'
    )

def generate_dashboard(log):
    entries_html = ""
    platforms = ["blog", "twitter", "threads", "reddit", "medium"]

    for entry in reversed(log):
        status = entry["status"]
        content = entry["content"]

        badges = (
            make_badge("Shopify", status["shopify"]) +
            make_badge("Twitter", status["twitter"]) +
            make_badge("Threads", status["threads"]) +
            make_badge("Reddit", status["reddit"]) +
            make_badge("Medium", status["medium"])
        )

        tab_buttons = "".join([make_tab_button(entry["id"], p) for p in platforms])
        tab_contents = "".join([make_tab_content(entry["id"], p, content[p]) for p in platforms])

        shopify_link = ""
        if entry["shopify_url"]:
            shopify_link = (
                '<a href="' + entry["shopify_url"] + '" target="_blank" '
                'style="color:#f5c518;">View on Shopify</a>'
            )

        entries_html += (
            '<div style="background:#111;border:1px solid #222;border-radius:12px;'
            'padding:24px;margin-bottom:24px;">'

            '<div style="display:flex;justify-content:space-between;'
            'align-items:flex-start;margin-bottom:12px;">'
            '<div>'
            '<div style="color:#888;font-size:12px;margin-bottom:4px;">'
            '#' + str(entry["id"]) + ' · ' + entry["date"] + '</div>'
            '<h2 style="margin:0;font-size:18px;color:white;">' + entry["topic"].title() + '</h2>'
            '<div style="margin-top:6px;color:#666;font-size:12px;">' + entry.get("keywords", "") + '</div>'
            '</div>'
            '<div>' + shopify_link + '</div>'
            '</div>'

            '<div style="margin-bottom:12px;">' + badges + '</div>'

            '<div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">'
            + tab_buttons +
            '</div>'

            + tab_contents +
            '</div>'
        )

    total = len(log)
    shopify_live = sum(1 for e in log if e["status"]["shopify"])
    auto_open_js = " ".join(["showTab(" + str(e["id"]) + ", 'blog');" for e in log])

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Outkast Content Hub</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0a0a0a; color: white; font-family: -apple-system, sans-serif; padding: 24px; }
        h1 { font-size: 28px; margin-bottom: 4px; }
        pre { overflow-x: auto; }
    </style>
</head>
<body>
<div style="max-width:900px;margin:0 auto;">
    <div style="margin-bottom:32px;">
        <h1>😈 Outkast Content Hub</h1>
        <p style="color:#666;margin-top:6px;">Your automated blog engine dashboard</p>
        <div style="display:flex;gap:24px;margin-top:16px;">
            <div style="background:#111;padding:16px 24px;border-radius:10px;border:1px solid #222;">
                <div style="font-size:28px;font-weight:bold;color:#f5c518;">""" + str(total) + """</div>
                <div style="color:#666;font-size:13px;">Total Blogs</div>
            </div>
            <div style="background:#111;padding:16px 24px;border-radius:10px;border:1px solid #222;">
                <div style="font-size:28px;font-weight:bold;color:#00c853;">""" + str(shopify_live) + """</div>
                <div style="color:#666;font-size:13px;">Live on Shopify</div>
            </div>
            <div style="background:#111;padding:16px 24px;border-radius:10px;border:1px solid #222;">
                <div style="font-size:28px;font-weight:bold;color:#f5c518;">""" + str(total - shopify_live) + """</div>
                <div style="color:#666;font-size:13px;">Pending</div>
            </div>
        </div>
    </div>
    """ + (entries_html if entries_html else '<p style="color:#444;text-align:center;padding:60px;">No blogs yet.</p>') + """
</div>
<script>
    function showTab(id, platform) {
        ['blog','twitter','threads','reddit','medium'].forEach(p => {
            const el = document.getElementById('tab-' + id + '-' + p);
            const btn = document.getElementById('btn-' + id + '-' + p);
            if (el) el.style.display = 'none';
            if (btn) { btn.style.background = '#222'; btn.style.color = '#ccc'; }
        });
        const active = document.getElementById('tab-' + id + '-' + platform);
        const activeBtn = document.getElementById('btn-' + id + '-' + platform);
        if (active) active.style.display = 'block';
        if (activeBtn) { activeBtn.style.background = '#f5c518'; activeBtn.style.color = '#000'; }
    }
    function copyText(id) {
        const el = document.getElementById(id);
        navigator.clipboard.writeText(el.innerText).then(() => { alert('Copied!'); });
    }
    document.addEventListener('DOMContentLoaded', () => {
        """ + auto_open_js + """
    });
</script>
</body>
</html>"""

    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Dashboard generated -> open dashboard.html in your browser")

if __name__ == "__main__":
    if os.path.exists("generated_content.json"):
        with open("generated_content.json", "r", encoding="utf-8") as f:
            content = json.load(f)
        shopify_url = "https://outkastcode.myshopify.com/blogs/the-outkast-journal"
        log = save_to_log(content, shopify_url)
        generate_dashboard(log)
    else:
        print("No generated_content.json found. Run writer.py first.")