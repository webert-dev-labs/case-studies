"""Image metadata check called by the pre-commit hook.

Reads the staged version of each file given on the command line and prints one line per
file that carries image metadata: PNG chunks beyond pixels and colour basics (text, dates,
software names, EXIF, colour profiles that can name a device), in PNG files and in PNGs
embedded in HTML, Markdown or SVG. Prints nothing when every file is clean.

Fix a reported image by saving it again without metadata, for example with Pillow:
    Image.open(src).save(dst)    # Pillow writes no text chunks unless asked to
"""

import base64
import re
import struct
import subprocess
import sys

SAFE_CHUNKS = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"pHYs", b"sRGB", b"gAMA",
               b"cHRM", b"bKGD"}
SIGNATURE = b"\x89PNG\r\n\x1a\n"
EMBEDDED = re.compile(rb"data:image/png;base64,([A-Za-z0-9+/=]+)")


def metadata_chunks(data: bytes) -> list[str]:
    found, i = [], len(SIGNATURE)
    while i + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[i:i + 8])
        if kind not in SAFE_CHUNKS and kind.decode("latin-1") not in found:
            found.append(kind.decode("latin-1"))
        i += 12 + length
        if kind == b"IEND":
            break
    return found


def main(paths: list[str]) -> None:
    for path in paths:
        data = subprocess.run(
            ["git", "cat-file", "blob", f":{path}"], capture_output=True, check=True
        ).stdout
        if data.startswith(SIGNATURE):
            chunks = metadata_chunks(data)
            if chunks:
                print(f"[image metadata: {', '.join(chunks)}] {path}")
            continue
        if b"\0" in data[:8000]:
            continue
        chunks = []
        for match in EMBEDDED.finditer(data):
            try:
                embedded = base64.b64decode(match.group(1))
            except ValueError:
                continue
            if embedded.startswith(SIGNATURE):
                chunks += [c for c in metadata_chunks(embedded) if c not in chunks]
        if chunks:
            print(f"[embedded image metadata: {', '.join(chunks)}] {path}")


if __name__ == "__main__":
    main(sys.argv[1:])
