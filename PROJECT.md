# NWC3373 — Cryptography System: Build Instructions for Claude Code

> This file is a complete build blueprint. Read every section before writing any code.
> Goal: build a working Flask web app implementing Galois LFSR (stream cipher) and a custom Feistel block cipher, with performance benchmarking. Deploy-ready for Render.

---

## Project Overview

**Course:** Fundamentals of Cryptography (NWC3373/NWC3193)  
**Framework:** Python + Flask  
**Deployment target:** Render (free tier)  
**Language:** Python 3.11  

The system must allow users to:
1. Encrypt and decrypt text messages using either cipher
2. Encrypt and decrypt uploaded files using either cipher
3. Run a performance benchmark across 1 KB, 100 KB, and 1 MB files
4. View algorithm descriptions and group info

---

## Final Project Structure

```
NWC3373-CryptoSystem/
│
├── app.py                        # Flask app — all routes
├── requirements.txt              # Dependencies
├── Procfile                      # Render start command
├── runtime.txt                   # Python version for Render
│
├── ciphers/
│   ├── __init__.py               # Empty init
│   ├── galois_lfsr.py            # Stream cipher implementation
│   └── feistel.py                # Block cipher implementation
│
├── benchmark/
│   ├── __init__.py               # Empty init
│   └── run_tests.py              # Performance timing logic
│
├── templates/
│   ├── base.html                 # Shared navbar + layout
│   ├── index.html                # Encrypt page (/)
│   ├── decrypt.html              # Decrypt page (/decrypt)
│   ├── performance.html          # Benchmark page (/performance)
│   └── about.html                # About page (/about)
│
├── static/
│   ├── style.css                 # Global styles
│   └── chart.js                  # Performance chart logic (vanilla JS + Chart.js CDN)
│
└── uploads/                      # Temp folder for file handling (auto-created)
```

---

## File 1: `requirements.txt`

```
flask
gunicorn
matplotlib
```

---

## File 2: `Procfile`

```
web: gunicorn app:app
```

---

## File 3: `runtime.txt`

```
python-3.11.0
```

---

## File 4: `ciphers/galois_lfsr.py` — Stream Cipher

Implement a **Galois LFSR-based stream cipher**. This is the A1 stream cipher requirement.

### Specification

- Register size: 32 bits
- Feedback polynomial: x^32 + x^22 + x^2 + x^1 + 1
  - Tap positions (0-indexed from right): bits 0, 1, 21, 31
- Key derivation: derive a 32-bit seed from the user's key string using a simple hash (sum of ord values mod 2^32)
- Keystream: generate one bit per clock cycle using Galois feedback method
- Encryption: XOR each byte of plaintext with one byte of keystream (8 bits at a time)
- Decryption: identical to encryption (XOR is symmetric)

### Functions to implement

```python
def derive_seed(key: str) -> int:
    """Derive a 32-bit integer seed from a string key."""

def generate_keystream(seed: int, length: int) -> bytes:
    """
    Generate `length` bytes of keystream using Galois LFSR.
    Tap positions: 0, 1, 21, 31 (these are the XOR feedback positions).
    Collect 8 bits per byte of output.
    Returns bytes object.
    """

def encrypt(plaintext: bytes, key: str) -> bytes:
    """XOR plaintext bytes with keystream. Returns ciphertext bytes."""

def decrypt(ciphertext: bytes, key: str) -> bytes:
    """XOR ciphertext bytes with keystream. Returns plaintext bytes (identical to encrypt)."""

def encrypt_text(message: str, key: str) -> str:
    """Encrypt a UTF-8 string, return hex string of ciphertext."""

def decrypt_text(hex_ciphertext: str, key: str) -> str:
    """Decrypt a hex string ciphertext, return UTF-8 plaintext string."""

def encrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Encrypt raw file bytes. Returns encrypted bytes."""

def decrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Decrypt raw file bytes. Returns decrypted bytes."""
```

### Important notes for implementation
- The Galois LFSR feedback: at each step, if the output bit is 1, XOR the register with the polynomial mask. Then shift right by 1.
- Polynomial mask for taps [0,1,21,31]: `0x80200003`
- Always re-derive seed from scratch for each encrypt/decrypt call (do not carry state between calls)
- Add a module-level docstring explaining what Galois LFSR is and the polynomial used

---

## File 5: `ciphers/feistel.py` — Block Cipher

Implement a **custom Feistel block cipher** with a SIMON-inspired round function. This is the A2 block cipher requirement.

### Specification

- Block size: 64 bits (8 bytes)
- Key size: 128 bits derived from user key string
- Rounds: 10
- Round function: uses AND, XOR, and circular bit rotation (SIMON-inspired)
- Key schedule: derive 10 subkeys from master key

### Round function (SIMON-inspired, operates on 32-bit half-block)

```
f(x) = ((x <<< 1) AND (x <<< 8)) XOR (x <<< 2)
```
Where `<<<` is left circular rotation on a 32-bit value.

### Key schedule

Derive 10 x 32-bit subkeys from a 128-bit master key:
1. Derive master key: take user key string, encode to bytes, pad/truncate to 16 bytes, interpret as two 64-bit integers (left_key, right_key)
2. Subkey[0] = lower 32 bits of left_key
3. Subkey[i] = (Subkey[i-1] <<< 3) XOR (lower 32 bits of right_key >> i) XOR i  for i = 1..9
4. All values mod 2^32

### Encryption structure

```
Split 64-bit block into Left (32 bits) and Right (32 bits)
For each round i in 0..9:
    new_Left  = Right
    new_Right = Left XOR f(Right) XOR subkeys[i]
Output: concat(Left, Right)
```

### Decryption structure

```
Split 64-bit block into Left and Right
For each round i in 9..0 (reversed):
    new_Right = Left
    new_Left  = Right XOR f(Left) XOR subkeys[i]
Output: concat(Left, Right)
```

### Padding

Use PKCS#7 padding to make plaintext a multiple of 8 bytes before encryption. Strip padding after decryption.

### Functions to implement

```python
def rotate_left_32(val: int, shift: int) -> int:
    """Circular left rotation on 32-bit value."""

def round_function(x: int) -> int:
    """SIMON-inspired round function: ((x<<<1) AND (x<<<8)) XOR (x<<<2)"""

def derive_master_key(key: str) -> tuple[int, int]:
    """Derive two 64-bit integers from key string. Pad/truncate key to 16 bytes."""

def generate_subkeys(key: str) -> list[int]:
    """Return list of 10 x 32-bit subkeys."""

def pad(data: bytes) -> bytes:
    """PKCS#7 pad data to multiple of 8 bytes."""

def unpad(data: bytes) -> bytes:
    """Strip PKCS#7 padding."""

def encrypt_block(block: bytes, subkeys: list[int]) -> bytes:
    """Encrypt a single 8-byte block. Returns 8-byte encrypted block."""

def decrypt_block(block: bytes, subkeys: list[int]) -> bytes:
    """Decrypt a single 8-byte block. Returns 8-byte decrypted block."""

def encrypt(plaintext: bytes, key: str) -> bytes:
    """Pad plaintext, split into 8-byte blocks, encrypt each block. Returns ciphertext bytes."""

def decrypt(ciphertext: bytes, key: str) -> bytes:
    """Split into 8-byte blocks, decrypt each, unpad. Returns plaintext bytes."""

def encrypt_text(message: str, key: str) -> str:
    """Encrypt UTF-8 string, return hex string."""

def decrypt_text(hex_ciphertext: str, key: str) -> str:
    """Decrypt hex string, return UTF-8 string."""

def encrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Encrypt raw file bytes."""

def decrypt_file(input_bytes: bytes, key: str) -> bytes:
    """Decrypt raw file bytes."""
```

### Important notes
- Process file/message byte-by-byte in 8-byte blocks — do not load entire large files into a single variable if avoidable
- Add a module-level docstring explaining Feistel structure and the SIMON-inspired round function
- Include a comment above the round function explaining each operation mathematically

---

## File 6: `benchmark/run_tests.py` — Performance Testing

### What it does
- Auto-generate test files of 1 KB, 100 KB, and 1 MB with random bytes
- Time encryption and decryption for both ciphers on all three file sizes
- Return results as a structured dictionary

### Functions to implement

```python
import time
import os
import tempfile

def generate_test_data(size_bytes: int) -> bytes:
    """Generate random bytes of given size."""

def time_operation(func, *args) -> float:
    """
    Run func(*args) and return elapsed time in milliseconds.
    Use time.perf_counter() for precision.
    """

def run_benchmark(key: str = "benchmarkKey123") -> dict:
    """
    Run full benchmark. Returns dict structured as:
    {
        "lfsr": {
            "1kb":   {"encrypt_ms": float, "decrypt_ms": float},
            "100kb": {"encrypt_ms": float, "decrypt_ms": float},
            "1mb":   {"encrypt_ms": float, "decrypt_ms": float}
        },
        "feistel": {
            "1kb":   {"encrypt_ms": float, "decrypt_ms": float},
            "100kb": {"encrypt_ms": float, "decrypt_ms": float},
            "1mb":   {"encrypt_ms": float, "decrypt_ms": float}
        }
    }
    Round all float values to 2 decimal places.
    """
```

---

## File 7: `app.py` — Flask Application

### Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Render encrypt page |
| `/decrypt` | GET | Render decrypt page |
| `/performance` | GET | Render performance page |
| `/about` | GET | Render about page |
| `/api/encrypt/text` | POST | Encrypt a text message |
| `/api/decrypt/text` | POST | Decrypt a text message |
| `/api/encrypt/file` | POST | Encrypt an uploaded file |
| `/api/decrypt/file` | POST | Decrypt an uploaded file |
| `/api/benchmark` | POST | Run performance benchmark |

### API request/response formats

**POST `/api/encrypt/text`**
```json
Request:  { "message": "hello world", "key": "mykey", "algorithm": "lfsr" }
Response: { "success": true, "ciphertext": "a3f2b9...", "algorithm": "lfsr" }
```

**POST `/api/decrypt/text`**
```json
Request:  { "ciphertext": "a3f2b9...", "key": "mykey", "algorithm": "lfsr" }
Response: { "success": true, "plaintext": "hello world" }
Error:    { "success": false, "error": "Decryption failed. Wrong key or corrupted data." }
```

**POST `/api/encrypt/file`**
```json
Form data: file=<binary>, key=<string>, algorithm=<lfsr|feistel>
Response: encrypted file download as .enc file
```

**POST `/api/decrypt/file`**
```json
Form data: file=<binary .enc>, key=<string>, algorithm=<lfsr|feistel>
Response: decrypted file download with original extension stripped
```

**POST `/api/benchmark`**
```json
Request:  {} (no body needed)
Response: { "success": true, "results": { ...benchmark dict... } }
```

### Error handling
- Wrap all cipher operations in try/except
- Return `{ "success": false, "error": "..." }` on failure
- Never crash on bad input — always return a JSON error response

### File upload handling
```python
import tempfile, os
# Save uploaded file to a temp path, process it, then delete temp file
# Never store files permanently
```

---

## File 8: `templates/base.html` — Base Layout

Create a clean, professional HTML layout with:
- A navbar with the app name "CryptoSystem NWC3373" and a lock icon
- Navigation links: Encrypt, Decrypt, Performance, About
- Active link highlighting based on current page
- Include Chart.js CDN in head: `https://cdn.jsdelivr.net/npm/chart.js`
- Include your `static/style.css`
- A `{% block content %}{% endblock %}` for page content
- Responsive meta viewport tag
- Color scheme: use teal/green as primary (#1D9E75), purple as secondary (#534AB7)

---

## File 9: `templates/index.html` — Encrypt Page

Extends base.html. Two sections side by side (or stacked on mobile):

### Text encryption section
- Algorithm toggle: two buttons "Galois LFSR" and "Feistel Cipher" (one selected at a time)
- Key input: password type field
- Plaintext textarea
- Encrypt button → calls `/api/encrypt/text` via fetch()
- Output box: shows hex ciphertext
- Copy button for ciphertext

### File encryption section
- Same algorithm toggle + key field
- File input (accept any file)
- Encrypt button → submits form to `/api/encrypt/file`
- Downloads the .enc file automatically

### JavaScript behavior
- Use `fetch()` for text encryption (no page reload)
- Show loading state on button while waiting
- Display error messages if API returns `success: false`

---

## File 10: `templates/decrypt.html` — Decrypt Page

Extends base.html. Mirror of encrypt page.

### Text decryption section
- Algorithm selector + key input
- Ciphertext textarea (hex input)
- Decrypt button → calls `/api/decrypt/text`
- Output: shows recovered plaintext in green box on success, red error box on failure

### File decryption section
- Algorithm selector + key input
- File input (accepts .enc files)
- Decrypt button → submits to `/api/decrypt/file`
- Downloads decrypted file

---

## File 11: `templates/performance.html` — Performance Page

Extends base.html.

### Layout
- "Run Benchmark" button at top
- While running: show a spinner/loading message
- After completion:
  - A summary stats row: fastest encrypt time, slowest encrypt time
  - A results table with columns: File Size | LFSR Encrypt | LFSR Decrypt | Feistel Encrypt | Feistel Decrypt (all in ms)
  - A grouped bar chart using Chart.js showing encryption times side by side
  - A short technical paragraph explaining why LFSR is faster than Feistel

### JavaScript behavior
```javascript
// On button click:
// 1. Show loading spinner
// 2. POST to /api/benchmark
// 3. On response: populate table rows and render Chart.js bar chart
// 4. Chart: x-axis = [1KB, 100KB, 1MB], two datasets = LFSR encrypt and Feistel encrypt
// 5. Colors: LFSR = #1D9E75, Feistel = #534AB7
```

### Chart.js config skeleton
```javascript
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['1 KB', '100 KB', '1 MB'],
        datasets: [
            { label: 'Galois LFSR', backgroundColor: '#1D9E75', data: [...] },
            { label: 'Feistel Cipher', backgroundColor: '#534AB7', data: [...] }
        ]
    },
    options: { responsive: true, plugins: { legend: { position: 'top' } } }
});
```

---

## File 12: `templates/about.html` — About Page

Extends base.html.

### Sections
1. Algorithm descriptions:
   - Galois LFSR: 32-bit register, feedback polynomial, XOR keystream — explain in 3–4 sentences
   - Feistel cipher: 10-round SIMON-inspired, 64-bit block, key schedule — explain in 3–4 sentences

2. Group members table:
   - 3 rows: Member name | Role | Tasks
   - Leave names as placeholders: "Member 1", "Member 2", "Member 3"

3. GitHub link section:
   - Prominent button linking to GitHub repo
   - Placeholder URL: `https://github.com/your-group/NWC3373-CryptoSystem`

---

## File 13: `static/style.css`

Write clean, minimal CSS. Key rules:

```css
/* Color variables */
:root {
    --primary: #1D9E75;
    --primary-light: #E1F5EE;
    --secondary: #534AB7;
    --secondary-light: #EEEDFE;
    --danger: #E24B4A;
    --text: #1a1a1a;
    --text-muted: #6b6b6b;
    --border: #e0e0e0;
    --bg: #f8f8f6;
    --white: #ffffff;
}

/* Must have styles for: */
/* - navbar with brand + links */
/* - active nav link */
/* - .card: white box with border and border-radius */
/* - .btn-primary: teal filled button */
/* - .btn-secondary: white button with border */
/* - .algo-btn and .algo-btn.active: algorithm selector toggle */
/* - .result-box: monospace output area with light teal background */
/* - .result-box.error: red background for errors */
/* - .badge-stream: teal pill label */
/* - .badge-block: purple pill label */
/* - loading spinner */
/* - responsive: stack columns on mobile */
```

---

## Deployment Files Summary

After all code is written, verify these files exist in the root:

```
requirements.txt   → flask, gunicorn, matplotlib
Procfile           → web: gunicorn app:app
runtime.txt        → python-3.11.0
```

---

## Testing Checklist (run before pushing to GitHub)

Claude Code must verify each of the following works:

- [ ] `python -c "from ciphers.galois_lfsr import encrypt_text, decrypt_text; assert decrypt_text(encrypt_text('hello', 'key1'), 'key1') == 'hello'"`
- [ ] `python -c "from ciphers.feistel import encrypt_text, decrypt_text; assert decrypt_text(encrypt_text('hello world', 'key1'), 'key1') == 'hello world'"`
- [ ] `python -c "from benchmark.run_tests import run_benchmark; r = run_benchmark(); print(r)"`
- [ ] `flask run` starts without errors
- [ ] Navigate to `http://localhost:5000` — encrypt page loads
- [ ] Encrypt the text "Test message" with key "abc" using LFSR → get hex output
- [ ] Decrypt that hex output with same key → get "Test message" back
- [ ] Same test with Feistel cipher
- [ ] Upload a small text file, encrypt it, download .enc file
- [ ] Upload that .enc file, decrypt it, verify content matches original
- [ ] Click Run Benchmark on performance page → table and chart appear
- [ ] All 4 nav links work

---

## README.md to include in the repo

```markdown
# NWC3373 Cryptography System

Secure message and file encryption system implementing:
- **Stream cipher**: Galois LFSR (32-bit, feedback polynomial x³²+x²²+x²+x+1)
- **Block cipher**: Custom Feistel cipher with SIMON-inspired round function (10 rounds, 64-bit block)

## Live Demo
https://your-app.onrender.com

## Group Members
| Name | Role |
|------|------|
| Member 1 | Stream cipher + testing |
| Member 2 | Block cipher + performance |
| Member 3 | Flask integration + report |

## How to Run Locally
```bash
git clone https://github.com/your-group/NWC3373-CryptoSystem
cd NWC3373-CryptoSystem
pip install -r requirements.txt
flask run
```
Then open http://localhost:5000

## How to Deploy to Render
1. Push this repo to GitHub
2. Sign up at render.com with GitHub
3. New Web Service → select this repo
4. Start command: `gunicorn app:app`
5. Deploy — live in ~2 minutes

## Project Structure
See PROJECT.md for full build specification.
```

---

## Notes for Claude Code

1. Implement ciphers from scratch — do not use any cryptography libraries (pycryptodome, cryptography, etc.). The point is to show the algorithm manually.
2. Keep cipher logic in `ciphers/` completely separate from Flask routes in `app.py`.
3. All API endpoints must return JSON. Never return plain text from API routes.
4. The performance benchmark must use `time.perf_counter()` not `time.time()` for precision.
5. Test the round-trip (encrypt then decrypt) for both ciphers before considering them done.
6. Do not hardcode any keys — always take key as a parameter.
7. Comment every non-obvious line in the cipher files — this is academic work and comments earn marks.
