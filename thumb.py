#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
thumbnailer_v2.py
Rekurencyjne miniatury z paskiem postępu (tqdm) i EXIF-auto-rotacją.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

from PIL import Image, ExifTags
from tqdm import tqdm

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

# mapujemy klucz EXIF -> Orientation (różne wersje Pillow)
EXIF_ORIENTATION_TAG = next(
    (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Rekurencyjnie tworzy miniatury w katalogu 'thumbs' (z paskiem postępu)."
    )
    p.add_argument("src", type=Path, help="Katalog źródłowy")
    p.add_argument(
        "-s",
        "--size",
        type=int,
        default=200,
        help="Dłuższy bok miniatury (px, domyślnie 200)",
    )
    p.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Nadpisuj istniejące miniatury",
    )
    return p.parse_args()


def collect_images(src_root: Path) -> List[Path]:
    """Zbiera wszystkie pliki graficzne (pomija katalog thumbs)."""
    images: List[Path] = []
    for root, dirs, files in os.walk(src_root):
        root_path = Path(root)
        if root_path.name.lower() == "thumbs":
            dirs[:] = []  # nie zagłębiaj się
            continue
        for fn in files:
            p = root_path / fn
            if p.suffix.lower() in IMAGE_EXTS:
                images.append(p)
    return images


def auto_rotate(img: Image.Image) -> Image.Image:
    """Zwraca obraz obrócony wg EXIF."""
    if not hasattr(img, "_getexif") or img._getexif() is None:
        return img
    exif = img._getexif()
    if EXIF_ORIENTATION_TAG not in exif:
        return img
    orientation = exif[EXIF_ORIENTATION_TAG]
    method = {
        2: Image.FLIP_LEFT_RIGHT,
        3: Image.ROTATE_180,
        4: Image.FLIP_TOP_BOTTOM,
        5: Image.TRANSPOSE,
        6: Image.ROTATE_270,
        7: Image.TRANSVERSE,
        8: Image.ROTATE_90,
    }.get(orientation)
    return img.transpose(method) if method else img


def create_thumbnail(src: Path, dst: Path, size: int) -> None:
    try:
        with Image.open(src) as im:
            # EXIF auto rotate
            im = auto_rotate(im)
            # thumbnail zachowuje proporcje
            im.thumbnail((size, size))
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst, format="JPEG", quality=90)
    except Exception as e:
        print(f"[BŁĄD] {src}: {e}")


def main() -> None:
    args = parse_args()
    src_root = args.src.resolve()
    if not src_root.is_dir():
        print("⛔ Podana ścieżka nie jest katalogiem.")
        sys.exit(1)

    dst_root = src_root / "thumbs"

    images = collect_images(src_root)
    total = len(images)
    if total == 0:
        print("Brak obrazów do przetworzenia.")
        return

    # Pasek postępu
    with tqdm(total=total, unit="img", desc="Generuję miniatury") as bar:
        for src_file in images:
            rel = src_file.relative_to(src_root)
            dst_file = (dst_root / rel.parent / (src_file.name)).resolve()
            if dst_file.exists() and not args.force:
                bar.update()
                continue
            create_thumbnail(src_file, dst_file, args.size)
            bar.update()

    print("✅ Gotowe! Miniatury w:", dst_root)


if __name__ == "__main__":
    main()