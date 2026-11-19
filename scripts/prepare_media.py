#!/usr/bin/env python3
"""Export the supplied figures and one execution per task for the project page."""

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


SOURCE_NAMES = {
    "method": "overview_mask2_revised.pdf",
    "simulation": "qualitative_results_no_forerobo.pdf",
    "video": "video.mp4",
}

# Seconds in the original 25-fps video, after title/fade-in and before trial 2.
# Playback speed is unchanged; the source itself is labelled "5× Speed".
CLIPS = [
    ("pour-water", 58.36, 68.64),
    ("place-teabag", 114.20, 129.60),
    ("place-atomizer", 84.20, 97.08),
    ("lower-cover", 148.48, 166.20),
    ("close-drawer", 184.76, 194.60),
]

# Crop boxes for the supplied comparison PDF rasterized at 240 dpi.
# Four original method rows, two examples per task. No result pixels are retouched.
TASK_COLUMNS = [
    ("pour-water", 179, 652, 1127),
    ("place-teabag", 1146, 1620, 2094),
    ("place-atomizer", 2115, 2590, 3063),
    ("lower-cover", 3084, 3556, 4031),
    ("close-drawer", 4053, 4525, 5000),
]
METHOD_ROWS = [(128, 516), (520, 906), (910, 1284), (1288, 1674)]
METHOD_LABELS = ["TAX-Pose", "Imagination Policy", "GWM", "OG-Gaussian (Ours)"]


def run(command):
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size):
    for name in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise RuntimeError("DejaVu Sans is required to render comparison labels.")


def export_figures(sources, output, temporary):
    method_raster = temporary / "method"
    comparison_raster = temporary / "comparison"
    for key, raster in (("method", method_raster), ("simulation", comparison_raster)):
        run(["pdftoppm", "-r", "240", "-singlefile", "-png", str(sources[key]), str(raster)])

    with Image.open(method_raster.with_suffix(".png")) as image:
        clean = image.convert("RGB")
        clean.info.clear()
        clean.save(output / "method/overview.png", optimize=True)

    with Image.open(comparison_raster.with_suffix(".png")) as image:
        comparison = image.convert("RGB")
    if comparison.size != (5009, 1758):
        raise ValueError("Comparison PDF dimensions changed. Recheck all crop boxes.")

    # Reflow each task to four method columns × two example rows for web reading.
    cell_width, cell_height, gap, padding, header = 476, 390, 16, 20, 64
    width = 4 * cell_width + 3 * gap + 2 * padding
    height = header + 2 * cell_height + gap + 38
    label_font = font(27)
    footer_font = font(20)
    for task, left, middle, right in TASK_COLUMNS:
        canvas = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(canvas)
        for method_index, (top, bottom) in enumerate(METHOD_ROWS):
            x = padding + method_index * (cell_width + gap)
            color = "#2563a6" if method_index == 3 else "#293442"
            draw.text(
                (x + cell_width / 2, 28),
                METHOD_LABELS[method_index],
                anchor="mm",
                fill=color,
                font=label_font,
            )
            for example, (x0, x1) in enumerate(((left + 2, middle - 2), (middle + 2, right - 2))):
                panel = comparison.crop((x0, top, x1, bottom))
                panel = ImageOps.contain(panel, (cell_width, cell_height), Image.Resampling.LANCZOS)
                y = header + example * (cell_height + gap)
                canvas.paste(panel, (x + (cell_width - panel.width) // 2, y + (cell_height - panel.height) // 2))
                draw.rectangle((x, y, x + cell_width - 1, y + cell_height - 1), outline="#dce2e8")
        draw.text(
            (width / 2, height - 17),
            "Top: Example 1  ·  Bottom: Example 2",
            anchor="mm",
            fill="#6b7786",
            font=footer_font,
        )
        canvas.save(output / ("simulation/" + task + ".webp"), lossless=True, method=6)


def export_clips(sources, output, ffmpeg, ffprobe):
    reports = []
    for task, start, end in CLIPS:
        video = output / ("real-world/" + task + ".mp4")
        poster = output / ("real-world/" + task + ".jpg")
        duration = round(end - start, 2)
        run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-n",
            "-ss", str(start), "-i", str(sources["video"]), "-t", str(duration),
            "-map", "0:v:0", "-map", "0:a:0?",
            "-map_metadata", "-1", "-map_chapters", "-1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(video),
        ])
        run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-n",
            "-ss", "1.0", "-i", str(video), "-frames:v", "1",
            "-map_metadata", "-1", "-q:v", "2", str(poster),
        ])
        details = json.loads(subprocess.check_output([
            ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)
        ]))
        stream = next(item for item in details["streams"] if item["codec_type"] == "video")
        actual = float(stream["duration"])
        if abs(actual - duration) > 0.041:
            raise ValueError("Unexpected clip duration: " + task)
        if stream["codec_name"] != "h264" or stream["pix_fmt"] != "yuv420p":
            raise ValueError("Unexpected video codec: " + task)
        if stream["width"] != 854 or stream["height"] != 480:
            raise ValueError("Unexpected video dimensions: " + task)
        tags = details["format"].get("tags", {})
        allowed_tags = {"major_brand", "minor_version", "compatible_brands", "encoder"}
        if set(tags) - allowed_tags:
            raise ValueError("Unexpected source metadata in exported clip: " + task)
        reports.append({
            "task": task,
            "sourceStartSeconds": start,
            "sourceEndSecondsExclusive": end,
            "durationSeconds": actual,
            "selectedExecution": 1,
            "sourcePlaybackSpeed": "5x",
            "additionalSpeedChange": False,
            "video": "real-world/" + task + ".mp4",
            "poster": "real-world/" + task + ".jpg",
        })
        print(task + ": " + str(actual) + " s", flush=True)
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    sources = {key: args.source_dir / value for key, value in SOURCE_NAMES.items()}
    for path in sources.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    expected = [args.output_dir / "method/overview.png"]
    expected += [args.output_dir / ("simulation/" + task + ".webp") for task, *_ in TASK_COLUMNS]
    expected += [args.output_dir / ("real-world/" + task + suffix) for task, *_ in CLIPS for suffix in (".mp4", ".jpg")]
    expected.append(args.output_dir / "processing.json")
    if any(path.exists() for path in expected):
        raise FileExistsError("Use a fresh output directory to preserve existing assets.")
    for directory in ("method", "simulation", "real-world"):
        (args.output_dir / directory).mkdir(parents=True, exist_ok=True)
    hashes = {key: sha256(path) for key, path in sources.items()}
    with tempfile.TemporaryDirectory(prefix="og_gaussian_export_") as temporary:
        export_figures(sources, args.output_dir, Path(temporary))
        clips = export_clips(sources, args.output_dir, args.ffmpeg, args.ffprobe)
    report = {
        "sourceFiles": SOURCE_NAMES,
        "sourceSha256": hashes,
        "renderDpi": 240,
        "simulationLayout": "Four method columns and two example rows; original result pixels preserved.",
        "clips": clips,
    }
    (args.output_dir / "processing.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Media export complete.", flush=True)


if __name__ == "__main__":
    main()
