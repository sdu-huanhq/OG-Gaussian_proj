#!/usr/bin/env python3
"""Export the revised overview and successful demos to a fresh media directory."""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from prepare_media import run, sha256


SOURCE_NAMES = {"method": "overview_mask3.pdf", "video": "demo_revised.mp4"}
FPS = 24
# Frame intervals [start, end) in demo_revised.mp4, rechecked on 2026-11-18.
# Main tasks include both executions; exploratory clips end before failures.
CLIPS = [
    ("real-world", "pour-water", 1069, 1304, "Pour Water", 1),
    ("real-world", "pour-water", 1316, 1600, "Pour Water", 2),
    ("real-world", "place-teabag", 2268, 2612, "Place Teabag", 1),
    ("real-world", "place-teabag", 2624, 2987, "Place Teabag", 2),
    ("real-world", "place-atomizer", 1612, 1921, "Place Atomizer", 1),
    ("real-world", "place-atomizer", 1933, 2256, "Place Atomizer", 2),
    ("real-world", "lower-cover", 2999, 3424, "Lower Cover", 1),
    ("real-world", "lower-cover", 3436, 3786, "Lower Cover", 2),
    ("real-world", "close-drawer", 3804, 4040, "Close Drawer", 1),
    ("real-world", "close-drawer", 4052, 4307, "Close Drawer", 2),
    ("exploratory", "multiple-references", 4680, 4984, "Pour Water", 1),
    ("exploratory", "unseen-tasks", 4386, 4668, "Place Teabag", 1),
]


def probe(ffprobe, path):
    return json.loads(subprocess.check_output([
        ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--only-second-executions", action="store_true",
                        help="Export only the five second executions, without rendering the overview.")
    parser.add_argument("--videos-only", action="store_true",
                        help="Export video clips and posters without rendering the overview.")
    args = parser.parse_args()
    source_names = {"video": SOURCE_NAMES["video"]} if args.only_second_executions or args.videos_only else SOURCE_NAMES
    sources = {key: args.source_dir / name for key, name in source_names.items()}
    clips = [clip for clip in CLIPS if clip[-1] == 2] if args.only_second_executions else CLIPS
    for path in sources.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    encoders = subprocess.check_output([args.ffmpeg, "-hide_banner", "-encoders"], stderr=subprocess.DEVNULL, text=True)
    if "libx264 " not in encoders:
        raise RuntimeError("This FFmpeg build lacks libx264. Use --ffmpeg with an H.264-capable build.")
    source_video = next(
        stream for stream in probe(args.ffprobe, sources["video"])["streams"]
        if stream["codec_type"] == "video"
    )
    if (source_video["width"], source_video["height"], source_video["r_frame_rate"]) != (854, 480, "24/1"):
        raise ValueError("Source video changed. Recheck the frame intervals.")
    if args.output_dir.exists():
        raise FileExistsError("Use a fresh output directory to preserve existing assets.")
    directories = {clip[0] for clip in clips}
    if "method" in sources:
        directories.add("method")
    for directory in directories:
        (args.output_dir / directory).mkdir(parents=True)

    if "method" in sources:
        with tempfile.TemporaryDirectory(prefix="og_gaussian_revised_") as temporary:
            raster = Path(temporary) / "overview"
            run(["pdftoppm", "-r", "240", "-singlefile", "-png", str(sources["method"]), str(raster)])
            with Image.open(raster.with_suffix(".png")) as image:
                clean = image.convert("RGB")
                clean.info.clear()
                clean.save(args.output_dir / "method/overview.png", optimize=True)

    reports = []
    for group, task, start_frame, end_frame, weights_task, execution in clips:
        filename = task if execution == 1 else task + "-2"
        relative = Path(group) / filename
        video = args.output_dir / relative.with_suffix(".mp4")
        poster = args.output_dir / relative.with_suffix(".jpg")
        duration = (end_frame - start_frame) / FPS
        run([
            args.ffmpeg, "-hide_banner", "-loglevel", "error", "-n",
            "-ss", f"{start_frame / FPS:.12f}", "-i", str(sources["video"]),
            "-t", f"{duration:.12f}", "-map", "0:v:0", "-map", "0:a:0?",
            "-map_metadata", "-1", "-map_chapters", "-1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(video),
        ])
        run([
            args.ffmpeg, "-hide_banner", "-loglevel", "error", "-n",
            "-ss", "1", "-i", str(video), "-frames:v", "1",
            "-map_metadata", "-1", "-q:v", "2", str(poster),
        ])
        details = probe(args.ffprobe, video)
        stream = next(item for item in details["streams"] if item["codec_type"] == "video")
        if (stream["codec_name"], stream["pix_fmt"], stream["width"], stream["height"]) != ("h264", "yuv420p", 854, 480):
            raise ValueError("Unexpected video format: " + task)
        if int(stream["nb_frames"]) != end_frame - start_frame:
            raise ValueError("Unexpected frame count: " + task)
        if abs(float(stream["duration"]) - duration) > 0.001:
            raise ValueError("Unexpected clip duration: " + task)
        allowed_tags = {"major_brand", "minor_version", "compatible_brands", "encoder"}
        if set(details["format"].get("tags", {})) - allowed_tags:
            raise ValueError("Unexpected source metadata: " + task)
        reports.append({
            "group": group,
            "task": task,
            "sourceStartFrame": start_frame,
            "sourceEndFrameExclusive": end_frame,
            "sourceStartSeconds": start_frame / FPS,
            "sourceEndSecondsExclusive": end_frame / FPS,
            "durationSeconds": float(stream["duration"]),
            "weightsTrainingTask": weights_task,
            "selectedExecution": execution,
            "sourcePlaybackSpeed": "5x",
            "additionalSpeedChange": False,
            "video": relative.with_suffix(".mp4").as_posix(),
            "poster": relative.with_suffix(".jpg").as_posix(),
        })
        print(f"{task}, execution {execution}: {duration:.3f} s", flush=True)

    report = {
        "sourceFiles": source_names,
        "sourceSha256": {key: sha256(path) for key, path in sources.items()},
        "sourceFps": FPS,
        "failureCasesIncluded": False,
        "failureSectionStartFrame": 4984,
        "clips": reports,
    }
    if "method" in sources:
        report["renderDpi"] = 240
    (args.output_dir / "processing.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Revised media export complete.", flush=True)


if __name__ == "__main__":
    main()
