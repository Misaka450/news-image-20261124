"""Deterministic entrypoint that emits entry.png to /output/entry.png."""

from __future__ import annotations

import hashlib
import os
import struct
import zlib
from pathlib import Path

from PIL import Image

MAX_BYTES = 1_048_576


def verify_png_chunks(raw: bytes) -> None:
    """Validate PNG signature, every chunk CRC, and IEND termination."""
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG signature")
    pos = 8
    saw_iend = False
    while pos < len(raw):
        if pos + 12 > len(raw):
            raise ValueError("Truncated PNG chunk")
        length = struct.unpack(">I", raw[pos : pos + 4])[0]
        ctype = raw[pos + 4 : pos + 8]
        cdata = raw[pos + 8 : pos + 8 + length]
        crc_stored = struct.unpack(">I", raw[pos + 8 + length : pos + 12 + length])[0]
        crc_calc = zlib.crc32(ctype + cdata) & 0xFFFFFFFF
        if crc_stored != crc_calc:
            raise ValueError(f"CRC mismatch in chunk {ctype!r}")
        pos += 12 + length
        if ctype == b"IEND":
            saw_iend = True
            break
    if not saw_iend or pos != len(raw):
        raise ValueError("PNG does not terminate cleanly at IEND")


def main() -> None:
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    if not src.exists():
        import build

        build.build()

    raw = src.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError(f"entry.png exceeds {MAX_BYTES} bytes ({len(raw)})")
    verify_png_chunks(raw)

    with Image.open(src) as im:
        if im.size != (1024, 1024):
            raise ValueError(f"Expected 1024x1024, got {im.size}")

    out_dir = Path(os.environ.get("OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    dst.write_bytes(raw)

    dst_raw = dst.read_bytes()
    if dst_raw != raw:
        raise RuntimeError("Output copy is not byte-identical to source")

    md5 = hashlib.md5(dst_raw).hexdigest()
    print(f"Wrote {dst} ({len(dst_raw)} bytes, md5={md5}, 1024x1024, CRC OK)")


if __name__ == "__main__":
    main()
