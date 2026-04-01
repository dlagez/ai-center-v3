from __future__ import annotations

import mimetypes


def detect_mime_type(file_name: str) -> str | None:
    mime_type, _ = mimetypes.guess_type(file_name)
    return mime_type
