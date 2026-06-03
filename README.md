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
git clone https://github.com/MohdHakimFz/cryptosystem-nwc3373.git
cd cryptosystem-nwc3373
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

## User Guide

See **[TUTORIAL.md](TUTORIAL.md)** for step-by-step instructions on every feature (encrypt, decrypt, performance, keys, mobile navigation, and troubleshooting).

## Project Structure

See PROJECT.md for full build specification.
