import re
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps

from db import UPLOAD_DIR, BACKUP_DIR

# Two intentionally separate pools (per handoff): thumbs (fast) vs transcode (slow).
thumbnail_executor = ThreadPoolExecutor(max_workers=8)
transcode_executor = ThreadPoolExecutor(max_workers=2)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".tiff", ".tif", ".webp", ".bmp"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mts"}

THUMB_SIZE = 400
PREVIEW_SIZE = 1600


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (name or "").strip().lower()).strip("-")
    return s or "folder"


def file_type_for(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in IMAGE_EXTS:
        return "photo"
    if ext in VIDEO_EXTS:
        return "video"
    return "other"


def tenant_root(tenant_id: str) -> Path:
    return UPLOAD_DIR / tenant_id


def gallery_dir(tenant_id: str, gallery_folder: str, subfolder: str = "") -> Path:
    p = tenant_root(tenant_id) / gallery_folder
    if subfolder:
        p = p / subfolder
    return p


def cache_dir(gallery_id: str, kind: str) -> Path:
    return UPLOAD_DIR / ".cache" / kind / gallery_id


def _resize_to(src: Path, dst: Path, max_size: int, quality: int = 82):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        im.thumbnail((max_size, max_size), Image.LANCZOS)
        if im.mode in ("RGBA", "P", "LA"):
            im = im.convert("RGB")
        im.save(dst, "JPEG", quality=quality, optimize=True)


def generate_image_derivatives(gallery_id: str, subfolder_slug: str, filename: str, src_path: str):
    """Runs in thumbnail_executor. Returns True on success."""
    src = Path(src_path)
    if not src.exists():
        return False
    stem = Path(filename).stem
    thumb = cache_dir(gallery_id, "thumbs") / subfolder_slug / f"{stem}.jpg"
    preview = cache_dir(gallery_id, "previews") / subfolder_slug / f"{stem}.jpg"
    try:
        _resize_to(src, thumb, THUMB_SIZE, 78)
        _resize_to(src, preview, PREVIEW_SIZE, 85)
        return True
    except Exception as e:
        import logging
        logging.getLogger("studioapp").warning("thumb gen failed for %s: %s", filename, e)
        return False


def dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for f in path.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except OSError:
                pass
    return total


def remove_path(path: Path):
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists():
        try:
            path.unlink()
        except OSError:
            pass


def backup_gallery_dir(tenant_id: str, gallery_folder: str) -> Path:
    return BACKUP_DIR / tenant_id / gallery_folder
