"""Performance benchmarking for Galois LFSR and Feistel ciphers."""

import os
import secrets
import time

from ciphers import feistel, galois_lfsr

BENCHMARK_KEY = "benchmarkKey123"
ALL_SIZES = {
    "1kb": 1024,
    "100kb": 100 * 1024,
    "1mb": 1024 * 1024,
}


def get_benchmark_sizes() -> dict:
    """Use smaller set on Render to stay under HTTP timeouts on free tier."""
    if os.environ.get("RENDER") or os.environ.get("BENCHMARK_QUICK"):
        return {k: v for k, v in ALL_SIZES.items() if k != "1mb"}
    return dict(ALL_SIZES)


def generate_test_data(size_bytes: int) -> bytes:
    """Generate random bytes of given size."""
    return secrets.token_bytes(size_bytes)


def time_operation(func, *args) -> float:
    """
    Run func(*args) and return elapsed time in milliseconds.
    Uses time.perf_counter() for precision.
    """
    start = time.perf_counter()
    func(*args)
    end = time.perf_counter()
    return round((end - start) * 1000, 2)


def _benchmark_cipher(
    encrypt_fn,
    decrypt_fn,
    key: str,
    sizes: dict,
) -> dict:
    """Time encrypt/decrypt for all file sizes for one cipher."""
    results = {}
    for label, size in sizes.items():
        data = generate_test_data(size)
        t0 = time.perf_counter()
        encrypted = encrypt_fn(data, key)
        encrypt_ms = round((time.perf_counter() - t0) * 1000, 2)
        decrypt_ms = time_operation(decrypt_fn, encrypted, key)
        results[label] = {
            "encrypt_ms": encrypt_ms,
            "decrypt_ms": decrypt_ms,
        }
    return results


def run_benchmark(key: str = BENCHMARK_KEY) -> dict:
    """
    Run benchmark across configured test sizes (1 KB, 100 KB, and 1 MB locally).

    Returns timing dict for LFSR and Feistel encrypt/decrypt operations.
    """
    sizes = get_benchmark_sizes()
    return {
        "sizes": list(sizes.keys()),
        "lfsr": _benchmark_cipher(
            galois_lfsr.encrypt,
            galois_lfsr.decrypt,
            key,
            sizes,
        ),
        "feistel": _benchmark_cipher(
            feistel.encrypt,
            feistel.decrypt,
            key,
            sizes,
        ),
    }
