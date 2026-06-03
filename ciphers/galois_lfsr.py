"""
Galois LFSR-based stream cipher.

A Linear Feedback Shift Register (LFSR) generates a pseudo-random bit sequence
from a seed. In Galois (modular) configuration, feedback taps XOR into the
register when the output bit is 1, then the register shifts right.

Polynomial: x^32 + x^22 + x^2 + x + 1
Tap positions (0-indexed from LSB): 0, 1, 21, 31
Polynomial mask: 0x80200003
"""

POLYNOMIAL_MASK = 0x80200003
REGISTER_MASK = 0xFFFFFFFF


def derive_seed(key: str) -> int:
    """Derive a 32-bit integer seed from a string key."""
    total = sum(ord(c) for c in key)
    return total & REGISTER_MASK


def generate_keystream(seed: int, length: int) -> bytes:
    """
    Generate `length` bytes of keystream using Galois LFSR.

    At each clock cycle: output LSB, if 1 XOR register with polynomial mask,
    then shift register right. Collect 8 output bits per keystream byte.
    """
    register = seed & REGISTER_MASK
    keystream = bytearray(length)

    for byte_index in range(length):
        byte_val = 0
        for bit_index in range(8):
            output_bit = register & 1
            if output_bit:
                register ^= POLYNOMIAL_MASK
            register = (register >> 1) & REGISTER_MASK
            byte_val |= output_bit << bit_index
        keystream[byte_index] = byte_val

    return bytes(keystream)


def encrypt(plaintext: bytes, key: str) -> bytes:
    """XOR plaintext bytes with keystream. Returns ciphertext bytes."""
    seed = derive_seed(key)
    stream = generate_keystream(seed, len(plaintext))
    return bytes(p ^ k for p, k in zip(plaintext, stream))


def decrypt(ciphertext: bytes, key: str) -> bytes:
    """XOR ciphertext bytes with keystream (symmetric with encrypt)."""
    return encrypt(ciphertext, key)


def encrypt_text(message: str, key: str) -> str:
    """Encrypt a UTF-8 string, return hex string of ciphertext."""
    ciphertext = encrypt(message.encode("utf-8"), key)
    return ciphertext.hex()


def decrypt_text(hex_ciphertext: str, key: str) -> str:
    """Decrypt a hex string ciphertext, return UTF-8 plaintext string."""
    ciphertext = bytes.fromhex(hex_ciphertext.strip())
    plaintext = decrypt(ciphertext, key)
    return plaintext.decode("utf-8")


def encrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Encrypt raw file bytes. Returns encrypted bytes."""
    return encrypt(input_bytes, key)


def decrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Decrypt raw file bytes. Returns decrypted bytes."""
    return decrypt(input_bytes, key)
