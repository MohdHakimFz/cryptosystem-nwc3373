# Fernet file encryption guide

> **Note:** The NWC3373 **web app** uses custom Galois LFSR and Feistel ciphers (no `cryptography` library).  
> This folder is a **separate lab/demo** using industry-standard Fernet.

## Install

```bash
pip install cryptography
```

## 1. Generate and save a secret key

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # 32 bytes, url-safe base64

with open("examples/secret.key", "wb") as f:
    f.write(key)
```

- **Never commit** `secret.key` to Git (add to `.gitignore`).
- Anyone with this key can decrypt your files.
- To reuse the same key later, load it with `key = open("secret.key", "rb").read()`.

## 2. Encrypt a file

```python
from cryptography.fernet import Fernet

key = open("examples/secret.key", "rb").read()
fernet = Fernet(key)

with open("mydocument.pdf", "rb") as f:
    plaintext = f.read()

ciphertext = fernet.encrypt(plaintext)

with open("mydocument.pdf.enc", "wb") as f:
    f.write(ciphertext)
```

## 3. Decrypt a file

```python
from cryptography.fernet import Fernet

key = open("examples/secret.key", "rb").read()
fernet = Fernet(key)

with open("mydocument.pdf.enc", "rb") as f:
    ciphertext = f.read()

plaintext = fernet.decrypt(ciphertext)  # raises InvalidToken if wrong key

with open("mydocument_restored.pdf", "wb") as f:
    f.write(plaintext)
```

## 4. Test full flow (encrypt → decrypt)

Run the included demo (creates a sample file if needed):

```bash
cd "Cryptography System"
python examples/fernet_file_demo.py
```

Or use your own file:

```bash
python examples/fernet_file_demo.py --input "C:\path\to\test.txt"
```

The script checks that decrypted bytes **exactly match** the original file.

## 5. Measure performance

Use `time.perf_counter()` around encrypt/decrypt:

```python
import time

start = time.perf_counter()
ciphertext = fernet.encrypt(data)
encrypt_ms = (time.perf_counter() - start) * 1000

start = time.perf_counter()
plaintext = fernet.decrypt(ciphertext)
decrypt_ms = (time.perf_counter() - start) * 1000

print(f"Plain size:  {len(data):,} bytes")
print(f"Cipher size: {len(ciphertext):,} bytes")
print(f"Encrypt:     {encrypt_ms:.2f} ms")
print(f"Decrypt:     {decrypt_ms:.2f} ms")
```

The demo script prints all of this automatically in step `[5] Performance`.

## Your web app (custom ciphers)

| Task | Fernet (this guide) | CryptoSystem web app |
|------|---------------------|----------------------|
| Encrypt file | `fernet.encrypt(bytes)` | Upload on **Encrypt** page |
| Decrypt file | `fernet.decrypt(bytes)` | Upload `.enc` on **Decrypt** page |
| Benchmark | `fernet_file_demo.py` | **Performance** page |

Do **not** add Fernet to the main Flask app if your report requires manual cipher implementation.
