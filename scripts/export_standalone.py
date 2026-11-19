#!/usr/bin/env python3
"""Bundle the current project page, including all videos, into one offline HTML."""

import argparse
import base64
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


MEDIA_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".svg": "image/svg+xml",
    ".mp4": "video/mp4", ".webm": "video/webm",
}


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "OG-Gaussian-standalone.html")
    args = parser.parse_args()
    if args.output.resolve() == root / "index.html":
        raise ValueError("The export must not overwrite index.html.")

    def local_file(url):
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            raise ValueError("An offline export requires a local asset: " + url)
        path = (root / unquote(parsed.path)).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise FileNotFoundError(url)
        return path

    embedded = {}

    def embed(url):
        if not url or url.startswith("data:"):
            return url
        path = local_file(url)
        if path not in embedded:
            mime = MEDIA_TYPES.get(path.suffix.lower())
            if not mime:
                raise ValueError("Unsupported media type: " + str(path))
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            embedded[path] = "data:" + mime + ";base64," + encoded
        return embedded[path]

    # Evaluate the project's own JS configuration so shared caption values and
    # media arrays are preserved, without bundling commented-out asset examples.
    read_config = """
const fs = require('node:fs');
const vm = require('node:vm');
const context = { window: {} };
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), context, { timeout: 1000 });
process.stdout.write(JSON.stringify(context.window.OG_GAUSSIAN_CONTENT));
"""
    config = json.loads(subprocess.check_output([
        "node", "-e", read_config, str(root / "static/js/content.js")
    ], text=True))

    def embed_media(value):
        if isinstance(value, list):
            return [embed_media(item) for item in value]
        if isinstance(value, dict):
            return {
                key: embed(item) if key in {"src", "poster", "fullsize"} and isinstance(item, str)
                else embed_media(item)
                for key, item in value.items()
            }
        return value

    config = embed_media(config)
    html = (root / "index.html").read_text(encoding="utf-8")

    def inline_styles(match):
        css = local_file(match.group(1)).read_text(encoding="utf-8")
        if re.search(r"@import|url\s*\(", css, re.I):
            raise ValueError("CSS contains additional assets; embed them before exporting.")
        return "<style>\n" + css + "\n</style>"

    html, styles_count = re.subn(r'<link rel="stylesheet" href="([^"]+)"\s*>', inline_styles, html)
    html, icon_count = re.subn(
        r'(<link rel="icon"[^>]*href=")([^"]+)("[^>]*>)',
        lambda match: match.group(1) + embed(match.group(2)) + match.group(3), html,
    )
    html, scripts_count = re.subn(r'<script defer src="static/js/(?:content|index)\.js[^\"]*"></script>', "", html)
    if (styles_count, icon_count, scripts_count) != (1, 1, 2):
        raise ValueError("Page asset tags changed; review the standalone bundler.")
    html = html.replace(
        "<!-- Edit content.js to connect the anonymous code repository and all media. -->",
        "<!-- Standalone snapshot. Regenerate with scripts/export_standalone.py after editing the source page. -->",
    )
    config_js = "window.OG_GAUSSIAN_CONTENT = " + json.dumps(config, ensure_ascii=False, separators=(",", ":")) + ";"
    app_js = (root / "static/js/index.js").read_text(encoding="utf-8")
    script = re.sub(r"</script", lambda _: "<\\/script", config_js + "\n" + app_js, flags=re.I)
    # Inline scripts cannot use defer: execute after all required DOM nodes exist.
    html = html.replace("</body>", "<script>\n" + script + "\n</script>\n</body>")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Exported {args.output} ({args.output.stat().st_size / 1024 / 1024:.1f} MiB; {len(embedded)} embedded assets).")


if __name__ == "__main__":
    main()
