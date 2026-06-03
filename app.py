"""Flask web application for the NWC3373 Cryptography System."""

import os
import secrets
import tempfile

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
from werkzeug.utils import secure_filename

from benchmark.run_tests import run_benchmark
from ciphers import feistel, galois_lfsr
from ciphers.envelope import (
    WRONG_KEY_ERROR,
    unwrap_file_payload,
    unwrap_text_payload,
    wrap_file_payload,
    wrap_text_payload,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CIPHERS = {
    "lfsr": {
        "encrypt": galois_lfsr.encrypt,
        "decrypt": galois_lfsr.decrypt,
    },
    "feistel": {
        "encrypt": feistel.encrypt,
        "decrypt": feistel.decrypt,
    },
}


def _get_cipher(algorithm: str):
    cipher = CIPHERS.get(algorithm)
    if cipher is None:
        raise ValueError("Invalid algorithm. Use 'lfsr' or 'feistel'.")
    return cipher


def _decryption_error_response():
    return jsonify({"success": False, "error": WRONG_KEY_ERROR}), 400


def _static_version(filename: str) -> int:
    path = os.path.join(STATIC_DIR, filename)
    if os.path.isfile(path):
        return int(os.path.getmtime(path))
    return 1


@app.context_processor
def inject_asset_version():
    return {"asset_v": _static_version("favicon.ico")}


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        STATIC_DIR,
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
        max_age=86400,
    )


def _is_wrong_key_error(exc: ValueError) -> bool:
    message = str(exc).lower()
    return (
        str(exc) == WRONG_KEY_ERROR
        or "pkcs#7" in message
        or "padding" in message
        or "block size" in message
        or "cannot unpad" in message
    )


@app.route("/")
def index():
    return render_template("index.html", active_page="encrypt")


@app.route("/decrypt")
def decrypt_page():
    return render_template("decrypt.html", active_page="decrypt")


@app.route("/performance")
def performance_page():
    return render_template("performance.html", active_page="performance")


@app.route("/about")
def about_page():
    return render_template("about.html", active_page="about")


@app.route("/api/encrypt/text", methods=["POST"])
def api_encrypt_text():
    try:
        data = request.get_json(force=True) or {}
        message = data.get("message", "")
        key = data.get("key", "")
        algorithm = data.get("algorithm", "lfsr")

        if not message:
            return jsonify({"success": False, "error": "Message is required."}), 400
        if not key:
            return jsonify({"success": False, "error": "Key is required."}), 400

        cipher = _get_cipher(algorithm)
        payload = wrap_text_payload(message)
        ciphertext = cipher["encrypt"](payload, key).hex()
        return jsonify({"success": True, "ciphertext": ciphertext, "algorithm": algorithm})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/decrypt/text", methods=["POST"])
def api_decrypt_text():
    try:
        data = request.get_json(force=True) or {}
        ciphertext = data.get("ciphertext", "")
        key = data.get("key", "")
        algorithm = data.get("algorithm", "lfsr")

        if not ciphertext:
            return jsonify({"success": False, "error": "Ciphertext is required."}), 400
        if not key:
            return jsonify({"success": False, "error": "Key is required."}), 400

        cipher = _get_cipher(algorithm)
        raw = bytes.fromhex(ciphertext.strip())
        decrypted = cipher["decrypt"](raw, key)
        plaintext = unwrap_text_payload(decrypted)
        return jsonify({"success": True, "plaintext": plaintext})
    except ValueError as exc:
        if _is_wrong_key_error(exc):
            return _decryption_error_response()
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception:
        return _decryption_error_response()


@app.route("/api/encrypt/file", methods=["POST"])
def api_encrypt_file():
    temp_path = None
    try:
        uploaded = request.files.get("file")
        key = request.form.get("key", "")
        algorithm = request.form.get("algorithm", "lfsr")

        if not uploaded or not uploaded.filename:
            return jsonify({"success": False, "error": "File is required."}), 400
        if not key:
            return jsonify({"success": False, "error": "Key is required."}), 400

        cipher = _get_cipher(algorithm)
        filename = secure_filename(uploaded.filename) or "file"
        temp_path = os.path.join(tempfile.gettempdir(), f"enc_{filename}")
        uploaded.save(temp_path)

        with open(temp_path, "rb") as handle:
            raw = handle.read()
        payload = wrap_file_payload(raw)
        encrypted = cipher["encrypt"](payload, key)

        out_path = os.path.join(tempfile.gettempdir(), f"{filename}.enc")
        with open(out_path, "wb") as handle:
            handle.write(encrypted)

        return send_file(
            out_path,
            as_attachment=True,
            download_name=f"{filename}.enc",
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/api/decrypt/file", methods=["POST"])
def api_decrypt_file():
    temp_path = None
    out_path = None
    try:
        uploaded = request.files.get("file")
        key = request.form.get("key", "")
        algorithm = request.form.get("algorithm", "lfsr")

        if not uploaded or not uploaded.filename:
            return jsonify({"success": False, "error": "File is required."}), 400
        if not key:
            return jsonify({"success": False, "error": "Key is required."}), 400

        cipher = _get_cipher(algorithm)
        filename = secure_filename(uploaded.filename) or "file.enc"
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        uploaded.save(temp_path)

        with open(temp_path, "rb") as handle:
            raw = handle.read()

        decrypted = cipher["decrypt"](raw, key)
        plaintext = unwrap_file_payload(decrypted)

        if filename.endswith(".enc"):
            download_name = filename[:-4]
        else:
            download_name = f"decrypted_{filename}"

        out_path = os.path.join(tempfile.gettempdir(), download_name)
        with open(out_path, "wb") as handle:
            handle.write(plaintext)

        return send_file(out_path, as_attachment=True, download_name=download_name)
    except ValueError:
        return _decryption_error_response()
    except Exception:
        return _decryption_error_response()
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/api/generate-key", methods=["GET"])
def api_generate_key():
    """Return a cryptographically secure random key for LFSR/Feistel."""
    try:
        key = secrets.token_urlsafe(24)
        return jsonify({"success": True, "key": key})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/benchmark", methods=["POST"])
def api_benchmark():
    try:
        results = run_benchmark()
        return jsonify({"success": True, "results": results})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True)
