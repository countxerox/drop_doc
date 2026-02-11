from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "txt",
    "rtf",
    "odt",
    "md",
    "csv",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


@app.get("/")
def index():
    return render_template("index.html", max_size_mb=MAX_CONTENT_LENGTH // (1024 * 1024))


@app.post("/upload")
def upload():
    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files were uploaded."}), 400

    uploaded = []
    rejected = []

    for file in files:
        original_name = file.filename or ""

        if not original_name:
            continue

        if not allowed_file(original_name):
            rejected.append({"file": original_name, "reason": "Unsupported file type"})
            continue

        safe_name = secure_filename(original_name)
        unique_name = f"{uuid4().hex}_{safe_name}"
        destination = UPLOAD_DIR / unique_name
        file.save(destination)

        uploaded.append(
            {
                "file": original_name,
                "stored_as": unique_name,
                "size_bytes": destination.stat().st_size,
            }
        )

    if not uploaded and rejected:
        return jsonify({"error": "All files were rejected.", "rejected": rejected}), 400

    return jsonify({"uploaded": uploaded, "rejected": rejected}), 201


@app.errorhandler(413)
def too_large(_):
    return (
        jsonify({"error": f"Upload too large. Max file size is {MAX_CONTENT_LENGTH // (1024 * 1024)} MB."}),
        413,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
