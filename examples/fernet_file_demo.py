"""
Standalone demo: Fernet file encryption (cryptography library).

NOT used by the NWC3373 web app (course project uses custom ciphers).
Install: pip install cryptography

Run:
  python examples/fernet_file_demo.py
  python examples/fernet_file_demo.py --input path/to/file.pdf
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

# Paths relative to project root
ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "examples" / "secret.key"
SAMPLE_FILE = ROOT / "examples" / "sample_plaintext.txt"
ENCRYPTED_FILE = ROOT / "examples" / "sample_plaintext.txt.enc"
DECRYPTED_FILE = ROOT / "examples" / "sample_plaintext.decrypted.txt"


def generate_and_save_key(key_path: Path = KEY_FILE) -> bytes:
    """1. Generate a Fernet key and save it to disk."""
    key = Fernet.generate_key()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(key)
    print(f"[1] Secret key saved: {key_path}")
    print(f"    Key (base64, keep private): {key.decode()}")
    return key


def load_key(key_path: Path = KEY_FILE) -> bytes:
    """Load an existing key from disk."""
    if not key_path.is_file():
        raise FileNotFoundError(
            f"Key not found at {key_path}. Run this script once to generate it."
        )
    return key_path.read_bytes()


def encrypt_file(
    input_path: Path,
    output_path: Path,
    key: bytes,
) -> tuple[float, int, int]:
    """2. Encrypt a file. Returns (seconds, plain_size, cipher_size)."""
    fernet = Fernet(key)
    plaintext = input_path.read_bytes()
    plain_size = len(plaintext)

    start = time.perf_counter()
    ciphertext = fernet.encrypt(plaintext)
    elapsed = time.perf_counter() - start

    output_path.write_bytes(ciphertext)
    cipher_size = len(ciphertext)
    return elapsed, plain_size, cipher_size


def decrypt_file(
    input_path: Path,
    output_path: Path,
    key: bytes,
) -> tuple[float, int]:
    """3. Decrypt a file. Returns (seconds, output_size)."""
    fernet = Fernet(key)
    ciphertext = input_path.read_bytes()

    start = time.perf_counter()
    try:
        plaintext = fernet.decrypt(ciphertext)
    except InvalidToken as exc:
        raise ValueError(
            "Decryption failed: wrong key or corrupted/tampered file."
        ) from exc
    elapsed = time.perf_counter() - start

    output_path.write_bytes(plaintext)
    return elapsed, len(plaintext)


def create_sample_file(path: Path = SAMPLE_FILE) -> Path:
    """Create a small test file if none exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "NWC3373 Fernet demo file.\n"
        "This plaintext will be encrypted and decrypted.\n" * 50
    )
    path.write_text(content, encoding="utf-8")
    print(f"    Created sample file: {path} ({path.stat().st_size} bytes)")
    return path


def run_full_flow(input_path: Path | None = None) -> None:
    """4 & 5. Encrypt → decrypt round-trip and print performance stats."""
    print("=" * 60)
    print("Fernet file encryption demo")
    print("=" * 60)

    # 1. Key
    if KEY_FILE.is_file():
        key = load_key()
        print(f"[1] Loaded existing key: {KEY_FILE}")
    else:
        key = generate_and_save_key()

    # Sample input
    plain_path = input_path or SAMPLE_FILE
    if not plain_path.is_file():
        print("\n[Setup] Creating sample plaintext...")
        plain_path = create_sample_file()

    enc_path = plain_path.with_suffix(plain_path.suffix + ".enc")
    dec_path = plain_path.with_name(plain_path.stem + ".decrypted" + plain_path.suffix)

    print(f"\n[Input]  {plain_path} ({plain_path.stat().st_size:,} bytes)")

    # 2. Encrypt
    enc_time, plain_size, cipher_size = encrypt_file(plain_path, enc_path, key)
    print(f"\n[2] Encrypted -> {enc_path}")
    print(f"    Ciphertext size: {cipher_size:,} bytes")

    # 3. Decrypt
    dec_time, out_size = decrypt_file(enc_path, dec_path, key)
    print(f"\n[3] Decrypted -> {dec_path}")
    print(f"    Output size: {out_size:,} bytes")

    # 4. Verify round-trip
    original = plain_path.read_bytes()
    recovered = dec_path.read_bytes()
    match = original == recovered
    print(f"\n[4] Round-trip check: {'PASS' if match else 'FAIL'}")
    if not match:
        raise SystemExit("Plaintext does not match after decrypt.")

    # 5. Performance summary
    print("\n[5] Performance")
    print("-" * 40)
    print(f"    Original file size:  {plain_size:>12,} bytes")
    print(f"    Encrypted file size: {cipher_size:>12,} bytes")
    overhead = cipher_size - plain_size
    print(f"    Size overhead:       {overhead:>12,} bytes (Fernet metadata + MAC)")
    print(f"    Encrypt time:        {enc_time * 1000:>12.2f} ms")
    print(f"    Decrypt time:        {dec_time * 1000:>12.2f} ms")
    print(f"    Total time:          {(enc_time + dec_time) * 1000:>12.2f} ms")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fernet file encrypt/decrypt demo")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="File to encrypt (default: examples/sample_plaintext.txt)",
    )
    parser.add_argument(
        "--generate-key-only",
        action="store_true",
        help="Only generate and save secret.key, then exit",
    )
    args = parser.parse_args()

    if args.generate_key_only:
        generate_and_save_key()
        return

    run_full_flow(args.input)


if __name__ == "__main__":
    main()
