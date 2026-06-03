# CryptoSystem NWC3373 — User Tutorial

Step-by-step guide for using the **CryptoSystem** web application.  
Covers every feature on the site: encrypt, decrypt, performance testing, appearance settings, and navigation.

---

## Before You Start

### Run the application locally

```bash
cd "Cryptography System"
pip install -r requirements.txt
python -m flask run
```

Open your browser at: **http://127.0.0.1:5000**

### What you need to know

| Topic | Detail |
|--------|--------|
| **Algorithms** | **Galois LFSR** (stream cipher) or **Feistel** (block cipher) |
| **Secret key** | Any text string — you must use the **same key** and **same algorithm** to decrypt |
| **Text output** | Hexadecimal (hex) string |
| **File output** | `.enc` encrypted file |

---

## Navigation

### Desktop (wide screen)

Use the top menu:

- **Encrypt** — protect messages and files  
- **Decrypt** — recover original data  
- **Performance** — speed comparison  
- **About** — algorithms and group info  

Use **Light** / **Dark** in the top-right to change theme.

### Mobile (phone / tablet)

- **Top bar:** app name + Light/Dark toggle  
- **Bottom bar:** Encrypt · Decrypt · Stats · About  

Tap a tab to switch pages. Scroll the main area to see forms and buttons.

---

## 1. Encrypt

Open **Encrypt** (home page: `/`).

This page has two cards: **Text Encryption** and **File Encryption**.

### 1.1 Choose an algorithm

Each card has two options:

| Button | Cipher type | Best for |
|--------|-------------|----------|
| **Galois LFSR** | Stream cipher | General text and files; often faster |
| **Feistel Cipher** | Block cipher | 64-bit blocks, 10 rounds, PKCS#7 padding |

Click one option — the active choice is highlighted.

> Use the **same algorithm** when you decrypt later.

### 1.2 Enter or generate a secret key

1. Type your own key in **Secret Key** — any letters or numbers (e.g. `ABC`, `mykey123`), **or**
2. Click **Generate** (attached to the input box) for a random key.

**Extra key tools:**

| Button | Action |
|--------|--------|
| **Generate** | Creates a random key and tries to copy it to your clipboard |
| **Copy** | Copies the current key |
| **Show** / **Hide** | Makes the key visible so you can select and copy it |

**Important:** Save your key somewhere safe. If you lose it, you cannot decrypt your data.

> You can also paste a key from another tool (e.g. a password generator). Any text string works.

### 1.3 Encrypt text

1. Select **Galois LFSR** or **Feistel Cipher**.
2. Enter or generate a **Secret Key**.
3. Type your message in **Plaintext Message**.
4. Click **Encrypt Text**.
5. The **Ciphertext (hex)** box shows the encrypted result.
6. Click **Copy** to copy the hex string (e.g. for email or notes).

**Example**

| Field | Value |
|-------|--------|
| Algorithm | Galois LFSR |
| Key | `abc` |
| Plaintext | `Test message` |
| Result | A long hex string (different each time for the same message is normal for stream ciphers) |

### 1.4 Encrypt a file

1. Select algorithm and **Secret Key** (same as for text).
2. Click the upload area or **drop a file** into it.
3. Click **Encrypt & Download**.
4. Your browser downloads `yourfilename.enc`.

Keep the **same key** and **algorithm** to decrypt this file later.

---

## 2. Decrypt

Open **Decrypt** (`/decrypt`).

### 2.1 Decrypt text

1. Select the **same algorithm** used for encryption.
2. Enter the **same Secret Key**.
3. Paste the **hex ciphertext** into **Ciphertext (hex)**.
4. Click **Decrypt Text**.
5. **Recovered Plaintext** shows the original message in green on success.

**If decryption fails**

- Red error: wrong key, wrong algorithm, or corrupted / incomplete hex  
- Check for extra spaces or missing characters in the hex string  

### 2.2 Decrypt a file

1. Select the **same algorithm** and **Secret Key** as when you encrypted.
2. Upload the `.enc` file (drag-and-drop or browse).
3. Click **Decrypt & Download**.
4. Open the downloaded file and confirm it matches the original.

---

## 3. Performance (Benchmark)

Open **Performance** (`/performance`) — on mobile this tab is labeled **Stats**.

### What it does

Runs automated tests on random data at three sizes:

| Size | Amount |
|------|--------|
| 1 KB | 1,024 bytes |
| 100 KB | 102,400 bytes |
| 1 MB | 1,048,576 bytes |

For each size it measures **encrypt** and **decrypt** time (milliseconds) for **both** ciphers.

### How to run

1. Go to the Performance page.
2. Click **Run Benchmark**.
3. Wait 10–30 seconds (1 MB tests take longer).
4. View:
   - **Summary cards** — fastest and slowest encrypt times  
   - **Results table** — all timings  
   - **Bar chart** — LFSR vs Feistel encrypt speed  

### How to read results

- **Lower milliseconds (ms) = faster**  
- LFSR is usually faster than Feistel on larger files (stream vs multi-round block processing)  
- Use these numbers in your report or presentation  

---

## 4. About

Open **About** (`/about`).

This page includes:

- **Galois LFSR** — short description (32-bit register, feedback polynomial, XOR keystream)  
- **Custom Feistel** — 10 rounds, SIMON-style round function, PKCS#7 padding  
- **Group members** — names, roles, tasks (update placeholders before submission)  
- **GitHub** — link to your repository  

---

## 5. Light and Dark Mode

1. Find **Light** and **Dark** in the top-right (desktop) or top bar (mobile).  
2. Click your preferred mode.  
3. The choice is saved in your browser and restored on the next visit.  

Charts, tables, and forms all follow the selected theme.

---

## 6. Quick end-to-end test (recommended)

Use this checklist before demo or submission.

### Text (LFSR)

1. **Encrypt** → LFSR, key `abc`, message `Hello NWC3373` → **Encrypt Text**  
2. Copy the hex output  
3. **Decrypt** → LFSR, key `abc`, paste hex → **Decrypt Text**  
4. Confirm you see `Hello NWC3373`  

### Text (Feistel)

Repeat with **Feistel Cipher** and message `Hello NWC3373`.

### File

1. Create a small `test.txt` file on your computer  
2. **Encrypt** → upload file, key `mykey123`, download `.enc`  
3. **Decrypt** → upload `.enc`, same key and algorithm → download restored file  
4. Open restored file — content should match original  

### Performance

1. **Performance** → **Run Benchmark**  
2. Confirm table and chart appear  

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| Page will not load | Run `python -m flask run` and open http://127.0.0.1:5000 |
| Decrypt shows error | Same **key** and **algorithm** as encrypt; check hex is complete |
| File decrypt fails | Same key/algorithm; file must be `.enc` from this app |
| Cannot copy key | Use **Copy**, **Show**, or **Generate** (auto-copy); on mobile long-press the visible key |
| Benchmark takes long | Normal for 1 MB; wait until loading finishes |
| Old layout on phone | Hard refresh: `Ctrl+Shift+R` (or clear browser cache) |

---

## 8. Optional: Fernet demo (not the main web app)

The course web app uses **custom LFSR and Feistel** ciphers only.

A separate command-line Fernet example lives in:

```bash
python examples/fernet_file_demo.py
```

See `examples/README_FERNET.md` for details. This is **optional** and not required for the main assignment UI.

---

## 9. Feature summary

| # | Feature | Page | Main actions |
|---|---------|------|----------------|
| 1 | Encrypt text | Encrypt | Algorithm, key, plaintext → hex |
| 2 | Encrypt file | Encrypt | Algorithm, key, file → `.enc` download |
| 3 | Decrypt text | Decrypt | Algorithm, key, hex → plaintext |
| 4 | Decrypt file | Decrypt | Algorithm, key, `.enc` → original file |
| 5 | Benchmark | Performance | Run tests, view table and chart |
| 6 | Algorithm info | About | Read documentation |
| 7 | Theme | All pages | Light / Dark toggle |
| 8 | Generate key | Encrypt / Decrypt | Generate, Copy, Show |

---

## 10. Report and demo tips

For lecturers or markers:

1. Show **Encrypt** with both algorithms.  
2. Show **Decrypt** round-trip with the same key.  
3. Show **Performance** chart and explain why LFSR is faster.  
4. Briefly explain keys: user-provided string → internal cipher state (not Fernet in the main app).  

For technical details and build specification, see **PROJECT.md**.  
For install and deployment, see **README.md**.

---

*NWC3373 — Fundamentals of Cryptography*
