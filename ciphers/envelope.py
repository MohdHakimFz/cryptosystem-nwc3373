"""
Payload envelope for verifying successful decryption.

A fixed magic header is prepended before encryption and checked after
decryption. Wrong keys produce garbage that fails the header check.
"""

FILE_HEADER = b"NWC3FLE1"
TEXT_HEADER = b"NWC3TXT1"

WRONG_KEY_ERROR = "Incorrect decryption key. Please try again."


def wrap_file_payload(data: bytes) -> bytes:
    """Prepend file magic header before cipher encryption."""
    return FILE_HEADER + data


def unwrap_file_payload(data: bytes) -> bytes:
    """Validate magic header after cipher decryption."""
    if not data.startswith(FILE_HEADER):
        raise ValueError(WRONG_KEY_ERROR)
    return data[len(FILE_HEADER) :]


def wrap_text_payload(message: str) -> bytes:
    """Prepend text magic header before cipher encryption."""
    return TEXT_HEADER + message.encode("utf-8")


def unwrap_text_payload(data: bytes) -> str:
    """Validate magic header and return UTF-8 message."""
    if not data.startswith(TEXT_HEADER):
        raise ValueError(WRONG_KEY_ERROR)
    try:
        return data[len(TEXT_HEADER) :].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(WRONG_KEY_ERROR) from exc
