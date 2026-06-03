"""
Custom Feistel block cipher with SIMON-inspired round function.

Feistel structure splits a 64-bit block into two 32-bit halves (Left, Right).
Each round updates: new_Left = Right, new_Right = Left XOR f(Right) XOR subkey.
Decryption reverses rounds using the same subkeys.

Block size: 64 bits (8 bytes)
Rounds: 10
Round function: f(x) = ((x <<< 1) AND (x <<< 8)) XOR (x <<< 2)
"""

BLOCK_SIZE = 8
NUM_ROUNDS = 10
WORD_MASK = 0xFFFFFFFF


def rotate_left_32(val: int, shift: int) -> int:
    """Circular left rotation on 32-bit value."""
    val &= WORD_MASK
    shift %= 32
    return ((val << shift) | (val >> (32 - shift))) & WORD_MASK


def round_function(x: int) -> int:
    """
    SIMON-inspired round function on 32-bit half-block.

    f(x) = ((x <<< 1) AND (x <<< 8)) XOR (x <<< 2)
    """
    x &= WORD_MASK
    return (rotate_left_32(x, 1) & rotate_left_32(x, 8)) ^ rotate_left_32(x, 2)


def derive_master_key(key: str) -> tuple[int, int]:
    """Derive two 64-bit integers from key string. Pad/truncate key to 16 bytes."""
    key_bytes = key.encode("utf-8")
    padded = (key_bytes + b"\x00" * 16)[:16]
    left_key = int.from_bytes(padded[:8], "big")
    right_key = int.from_bytes(padded[8:], "big")
    return left_key, right_key


def generate_subkeys(key: str) -> list[int]:
    """Return list of 10 x 32-bit subkeys."""
    left_key, right_key = derive_master_key(key)
    subkeys = [left_key & WORD_MASK]
    right_lower = right_key & WORD_MASK

    for i in range(1, NUM_ROUNDS):
        prev = subkeys[i - 1]
        rotated = rotate_left_32(prev, 3)
        shifted_right = (right_lower >> i) & WORD_MASK
        subkeys.append((rotated ^ shifted_right ^ i) & WORD_MASK)

    return subkeys


def pad(data: bytes) -> bytes:
    """PKCS#7 pad data to multiple of 8 bytes."""
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    if pad_len == 0:
        pad_len = BLOCK_SIZE
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes) -> bytes:
    """Strip PKCS#7 padding."""
    if not data:
        raise ValueError("Cannot unpad empty data")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid PKCS#7 padding")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid PKCS#7 padding bytes")
    return data[:-pad_len]


def _split_block(block: bytes) -> tuple[int, int]:
    """Split 8-byte block into two 32-bit halves (big-endian)."""
    left = int.from_bytes(block[:4], "big") & WORD_MASK
    right = int.from_bytes(block[4:], "big") & WORD_MASK
    return left, right


def _join_block(left: int, right: int) -> bytes:
    """Combine two 32-bit halves into 8-byte block."""
    return (
        (left & WORD_MASK).to_bytes(4, "big")
        + (right & WORD_MASK).to_bytes(4, "big")
    )


def encrypt_block(block: bytes, subkeys: list[int]) -> bytes:
    """Encrypt a single 8-byte block. Returns 8-byte encrypted block."""
    left, right = _split_block(block)

    for i in range(NUM_ROUNDS):
        new_left = right
        new_right = (left ^ round_function(right) ^ subkeys[i]) & WORD_MASK
        left, right = new_left, new_right

    return _join_block(left, right)


def decrypt_block(block: bytes, subkeys: list[int]) -> bytes:
    """Decrypt a single 8-byte block. Returns 8-byte decrypted block."""
    left, right = _split_block(block)

    for i in range(NUM_ROUNDS - 1, -1, -1):
        new_right = left
        new_left = (right ^ round_function(left) ^ subkeys[i]) & WORD_MASK
        left, right = new_left, new_right

    return _join_block(left, right)


def encrypt(plaintext: bytes, key: str) -> bytes:
    """Pad plaintext, encrypt each 8-byte block. Returns ciphertext bytes."""
    subkeys = generate_subkeys(key)
    padded = pad(plaintext)
    ciphertext = bytearray()

    for offset in range(0, len(padded), BLOCK_SIZE):
        block = padded[offset : offset + BLOCK_SIZE]
        ciphertext.extend(encrypt_block(block, subkeys))

    return bytes(ciphertext)


def decrypt(ciphertext: bytes, key: str) -> bytes:
    """Decrypt 8-byte blocks, then remove PKCS#7 padding."""
    if len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Ciphertext length must be a multiple of block size")

    subkeys = generate_subkeys(key)
    plaintext = bytearray()

    for offset in range(0, len(ciphertext), BLOCK_SIZE):
        block = ciphertext[offset : offset + BLOCK_SIZE]
        plaintext.extend(decrypt_block(block, subkeys))

    return unpad(bytes(plaintext))


def encrypt_text(message: str, key: str) -> str:
    """Encrypt UTF-8 string, return hex string."""
    return encrypt(message.encode("utf-8"), key).hex()


def decrypt_text(hex_ciphertext: str, key: str) -> str:
    """Decrypt hex string, return UTF-8 string."""
    ciphertext = bytes.fromhex(hex_ciphertext.strip())
    return decrypt(ciphertext, key).decode("utf-8")


def encrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Encrypt raw file bytes."""
    return encrypt(input_bytes, key)


def decrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Decrypt raw file bytes."""
    return decrypt(input_bytes, key)
