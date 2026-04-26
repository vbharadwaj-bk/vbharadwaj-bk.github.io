#!/usr/bin/env python3
"""Interactive image minifier with backup and revert support.

Usage:
- Minify images over 1024 KB (default):
    python minify.py
- Minify images over a custom threshold:
    python minify.py --threshold-kb 700
- Minify only files whose names contain a string:
    python minify.py --filter group
- Revert the most recent minify pass:
    python minify.py --revert

Behavior:
- Scans content/images recursively for JPG/JPEG/PNG files.
- Prompts for each file above the size threshold before minifying.
- Saves originals into original_images/ with collision-safe filenames.
- Writes run history to original_images/minify_log.json.
- Supports --revert to restore files from the most recent log.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image


DEFAULT_THRESHOLD_KB = 1024
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
SOURCE_DIR = Path("content/images")
ORIGINALS_DIR = Path("original_images")
LOG_FILE_NAME = "minify_log.json"


@dataclass
class Action:
    source: str
    backup: str
    operation: str
    old_size: int
    new_size: int
    reverted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "backup": self.backup,
            "operation": self.operation,
            "old_size": self.old_size,
            "new_size": self.new_size,
            "reverted": self.reverted,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minify large images in content/images with backup + revert support.",
    )
    parser.add_argument(
        "--threshold-kb",
        type=int,
        default=DEFAULT_THRESHOLD_KB,
        help=f"Only prompt for files larger than this many KB (default: {DEFAULT_THRESHOLD_KB}).",
    )
    parser.add_argument(
        "--revert",
        action="store_true",
        help="Revert the most recent minify pass from original_images/minify_log.json.",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Only consider images whose filename contains this string (case-insensitive).",
    )
    return parser.parse_args()


def bytes_to_kb(size_bytes: int) -> float:
    return size_bytes / 1024.0


def prompt_yes_no(question: str) -> bool:
    while True:
        answer = input(f"{question} [y/n]: ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer 'y' or 'n'.")


def display_path(path: Path) -> Path:
    """Return a path suitable for CLI display without raising on path style mismatch."""
    if not path.is_absolute():
        return path
    try:
        return path.relative_to(Path.cwd())
    except ValueError:
        return path


def find_candidate_images(
    source_dir: Path,
    threshold_bytes: int,
    filename_filter: str | None = None,
) -> list[Path]:
    if not source_dir.exists():
        print(f"Error: source directory not found: {source_dir}", file=sys.stderr)
        return []

    candidates: list[Path] = []
    lowered_filter = filename_filter.lower() if filename_filter else None
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        if lowered_filter and lowered_filter not in path.name.lower():
            continue
        if path.stat().st_size > threshold_bytes:
            candidates.append(path)
    return candidates


def unique_backup_path(originals_dir: Path, file_name: str) -> Path:
    stem = Path(file_name).stem
    suffix = Path(file_name).suffix
    candidate = originals_dir / f"{stem}{suffix}"
    index = 1
    while candidate.exists():
        candidate = originals_dir / f"{stem}_{index}{suffix}"
        index += 1
    return candidate


def minify_jpeg(path: Path, target_bytes: int) -> None:
    with Image.open(path) as image:
        image = image.convert("RGB")

        # Decrease quality in steps, then optionally downscale if still large.
        for quality in (85, 78, 72, 66, 60, 52, 45):
            image.save(path, format="JPEG", quality=quality, optimize=True)
            if path.stat().st_size <= target_bytes:
                return

        width, height = image.size
        resized = image
        for _ in range(4):
            width = max(1, int(width * 0.9))
            height = max(1, int(height * 0.9))
            resized = resized.resize((width, height), Image.Resampling.LANCZOS)
            resized.save(path, format="JPEG", quality=48, optimize=True)
            if path.stat().st_size <= target_bytes:
                return


def minify_png(path: Path, target_bytes: int) -> None:
    with Image.open(path) as image:
        image = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)

        # Start with optimized palette PNG.
        image.save(path, format="PNG", optimize=True)
        if path.stat().st_size <= target_bytes:
            return

        width, height = image.size
        resized = image
        for _ in range(6):
            width = max(1, int(width * 0.88))
            height = max(1, int(height * 0.88))
            resized = resized.resize((width, height), Image.Resampling.LANCZOS)
            resized.save(path, format="PNG", optimize=True)
            if path.stat().st_size <= target_bytes:
                return


def minify_image(path: Path, target_bytes: int) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        minify_jpeg(path, target_bytes)
        return "jpeg_quality"
    if suffix == ".png":
        minify_png(path, target_bytes)
        return "png_downscale"
    raise ValueError(f"Unsupported image type: {path}")


def log_file_path(originals_dir: Path) -> Path:
    return originals_dir / LOG_FILE_NAME


def load_history(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []

    try:
        payload = json.loads(log_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed log file: {log_path}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"Malformed log file: {log_path}")

    history = payload.get("history", [])
    if not isinstance(history, list):
        raise ValueError(f"Malformed log file: {log_path}")
    return history


def write_log(log_path: Path, data: dict[str, Any]) -> None:
    log_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_minify(threshold_kb: int, filename_filter: str | None) -> int:
    threshold_bytes = threshold_kb * 1024
    candidates = find_candidate_images(SOURCE_DIR, threshold_bytes, filename_filter)
    if not candidates:
        if filename_filter:
            print(
                f"No images above {threshold_kb} KB with names containing "
                f"'{filename_filter}' found in {SOURCE_DIR}."
            )
        else:
            print(f"No images above {threshold_kb} KB found in {SOURCE_DIR}.")
        return 0

    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)

    actions: list[Action] = []
    for image_path in candidates:
        rel_path = display_path(image_path)
        size_kb = bytes_to_kb(image_path.stat().st_size)
        should_minify = prompt_yes_no(
            f"Minify {rel_path} ({size_kb:.1f} KB > {threshold_kb} KB)?"
        )
        if not should_minify:
            continue

        backup_path = unique_backup_path(ORIGINALS_DIR, image_path.name)
        shutil.copy2(image_path, backup_path)

        old_size = image_path.stat().st_size
        operation = minify_image(image_path, threshold_bytes)
        new_size = image_path.stat().st_size

        actions.append(
            Action(
                source=str(image_path),
                backup=str(backup_path),
                operation=operation,
                old_size=old_size,
                new_size=new_size,
            )
        )
        print(
            "Minified "
            f"{rel_path}: {bytes_to_kb(old_size):.1f} KB -> {bytes_to_kb(new_size):.1f} KB"
        )

    log_path = log_file_path(ORIGINALS_DIR)
    try:
        history = load_history(log_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    log_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "threshold_kb": threshold_kb,
        "actions": [action.to_dict() for action in actions],
    }
    history.insert(0, log_entry)
    write_log(log_path, {"history": history})

    print(f"Wrote run log: {log_path}")
    print(f"Minified {len(actions)} image(s).")
    return 0


def run_revert() -> int:
    if not ORIGINALS_DIR.exists():
        print(
            f"Error: {ORIGINALS_DIR} not found; cannot revert without backup log.",
            file=sys.stderr,
        )
        return 1

    log_path = log_file_path(ORIGINALS_DIR)
    if not log_path.exists():
        print(
            f"Error: no minify log found in {ORIGINALS_DIR}; cannot revert.",
            file=sys.stderr,
        )
        return 1

    try:
        history = load_history(log_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not history:
        print(f"Error: log history is empty in {log_path}; cannot revert.", file=sys.stderr)
        return 1

    entry = history.pop(0)
    actions_data = entry.get("actions", [])
    if not isinstance(actions_data, list):
        print(f"Error: malformed log entry in {log_path}", file=sys.stderr)
        return 1

    reverted_count = 0
    for item in actions_data:
        source = Path(item["source"])
        backup = Path(item["backup"])
        if not backup.exists():
            print(f"Skipping missing backup: {backup}")
            continue

        source.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, source)
        reverted_count += 1
        print(f"Reverted: {source}")

    write_log(log_path, {"history": history})

    print(f"Popped latest log entry and updated: {log_path}")
    print(f"Reverted {reverted_count} image(s).")
    return 0


def main() -> int:
    args = parse_args()
    if args.threshold_kb <= 0:
        print("Error: --threshold-kb must be a positive integer.", file=sys.stderr)
        return 1

    if args.revert:
        return run_revert()
    return run_minify(args.threshold_kb, args.filter)


if __name__ == "__main__":
    raise SystemExit(main())