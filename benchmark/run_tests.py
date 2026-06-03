"""Performance benchmarking for Galois LFSR and Feistel ciphers."""

import secrets
import time

from ciphers import feistel, galois_lfsr

BENCHMARK_KEY = "benchmarkKey123"
SIZES = {
    "1kb": 1024,
    "100kb": 100 * 1024,
    "1mb": 1024 * 1024,
}


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
) -> dict:
    """Time encrypt/decrypt for all file sizes for one cipher."""
    results = {}
    for label, size in SIZES.items():
        data = generate_test_data(size)
        encrypted = encrypt_fn(data, key)
        results[label] = {
            "encrypt_ms": time_operation(encrypt_fn, data, key),
            "decrypt_ms": time_operation(decrypt_fn, encrypted, key),
        }
    return results


def run_benchmark(key: str = BENCHMARK_KEY) -> dict:
    """
    Run full benchmark across 1 KB, 100 KB, and 1 MB test data.

    Returns timing dict for LFSR and Feistel encrypt/decrypt operations.
    """
    return {
        "lfsr": _benchmark_cipher(
            galois_lfsr.encrypt,
            galois_lfsr.decrypt,
            key,
        ),
        "feistel": _benchmark_cipher(
            feistel.encrypt,
            feistel.decrypt,
            key,
        ),
    }
